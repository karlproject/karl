# Copyright (C) 2008-2009 Open Society Institute
#               Thomas Moroz: tmoroz@sorosny.org
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License Version 2 as published
# by the Free Software Foundation.  You may not use, modify or distribute
# this program under any other version of the GNU General Public License.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import email.message
import urllib

from formencode import Invalid
from formencode import validators
from repoze.bfg.chameleon_zpt import render_template
from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.security import authenticated_userid
from repoze.bfg.security import effective_principals
from repoze.bfg.security import has_permission
from repoze.bfg.url import model_url
from repoze.enformed import FormSchema
from repoze.lemonade.content import create_content
from repoze.lemonade.interfaces import IContent
from repoze.sendmail.interfaces import IMailDelivery
from repoze.who.plugins.zodb.users import get_sha_password
from webob.exc import HTTPFound
from zope.component.event import objectEventNotify
from zope.component import getMultiAdapter
from zope.component import getUtility

from karl.consts import countries
from karl.events import ObjectModifiedEvent
from karl.events import ObjectWillBeModifiedEvent
from karl.models.interfaces import ICatalogSearch
from karl.models.interfaces import IGridEntryInfo
from karl.models.interfaces import ILetterManager
from karl.models.interfaces import IProfile
from karl.security.interfaces import ISecurityWorkflow
from karl.utils import find_communities
from karl.utils import find_tags
from karl.utils import find_users
from karl.utils import get_setting
from karl.views import baseforms
from karl.views.api import TemplateAPI
from karl.views.batch import get_catalog_batch
from karl.views.login import logout_view
from karl.views.tags import get_tags_client_data
from karl.views.utils import convert_to_script
from karl.views.utils import CustomInvalid
from karl.views.utils import handle_photo_upload
from karl.views.form import render_form_to_response

def edit_profile_view(context, request):
    form = EditProfileForm(context=context)

    if 'form.cancel' in request.POST:
        return HTTPFound(location=model_url(context, request))

    if 'form.submitted' in request.POST:
        try:
            converted = form.validate(request.POST)
            objectEventNotify(ObjectWillBeModifiedEvent(context))

            # Handle simple fields
            for name in form.simple_field_names:
                setattr(context, name, converted.get(name))

            handle_photo_upload(context, converted, thumbnail=True)

            # Emit a modified event for recataloging
            objectEventNotify(ObjectModifiedEvent(context))

            path = model_url(context, request)
            msg = '?status_message=Profile%20edited'
            return HTTPFound(location=path+msg)

        except Invalid, e:
            fielderrors = e.error_dict
            fill_values = form.convert(request.POST)
            try:
                del fill_values['photo'] # filler cant handle photo field
            except KeyError:
                pass
    else:
        fielderrors = {}
        fill_values = {}

    page_title = 'Edit ' + context.title
    api = TemplateAPI(context, request, page_title)

    # Display portrait
    photo = context.get_photo()
    display_photo = {}
    if photo is not None:
        display_photo["url"] = model_url(photo, request)
        display_photo["may_delete"] = True
    else:
        display_photo["url"] = api.static_url + "/images/defaultUser.gif"
        display_photo["may_delete"] = False

    # Enable hiding of certain fields via CSS descendent selectors
    if api.user_is_staff:
        staff_role_classname = 'k3_staff_role'
    else:
        staff_role_classname = 'k3_nonstaff_role'

    staff_change_password_url = '%s?username=%s&email=%s&came_from=%s' % (
        get_setting(context, "staff_change_password_url"),
        urllib.quote_plus(context.__name__),
        urllib.quote_plus(context.email),
        urllib.quote_plus(api.here_url)
        )

    return render_form_to_response(
        'templates/edit_profile.pt',
        form,
        fill_values,
        post_url=request.url,
        formfields=api.formfields,
        fielderrors=fielderrors,
        api=api,
        photo=display_photo,
        staff_role_classname=staff_role_classname,
        staff_change_password_url=staff_change_password_url,
        )

class EditProfileForm(FormSchema):
    simple_field_names = [
        "firstname",
        "lastname",
        "email",
        "phone",
        "extension",
        "department",
        "position",
        "organization",
        "location",
        "country",
        "website",
        "languages",
        "office",
        "room_no",
        "biography",
    ]

    firstname = baseforms.firstname
    lastname = baseforms.lastname
    email = baseforms.email
    phone = baseforms.phone
    extension = baseforms.extension
    department = baseforms.department
    position = baseforms.position
    organization = baseforms.organization
    location = baseforms.location
    country = baseforms.country
    website = baseforms.website
    languages = baseforms.languages
    photo = baseforms.photo
    photo_delete = baseforms.photo_delete
    biography = baseforms.biography

    def from_python(self, values, state=None):
        # Convert model object to dict and then call super method
        if state is None:
            state = self._state
        context = state.context

        model_values = {}
        for name in self.simple_field_names:
            if hasattr(context, name):
                model_values[name] = getattr(context, name)

        model_values["photo"] = context.get("photo", None)
        model_values["photo_delete"] = False
        model_values.update(values)

        return super(EditProfileForm, self).from_python(model_values, state)

def get_group_fields(context):
    group_fields = []
    for group in get_setting(context, "selectable_groups").split():
        if group.startswith('group.'):
            title = group[6:]
        else:
            title = group
        # make the field name compatible with CSS
        fieldname = 'groupfield-%s' % group.replace('.', '-')
        group_fields.append({
            'group': group,
            'fieldname': fieldname,
            'title': title,
            })
    return group_fields

def admin_edit_profile_view(context, request):
    min_pw_length = get_setting(context, 'min_pw_length')
    form = AdminEditProfileForm(min_pw_length=min_pw_length,
                                context=context)
    group_fields = get_group_fields(context)
    for field in group_fields:
        validator = validators.Bool(if_missing=False, default=False)
        form.add_field(field['fieldname'], validator)

    users = find_users(context)
    userid = context.__name__
    user = users.get_by_id(userid)
    user_groups = set(user['groups'])

    if 'form.cancel' in request.POST:
        return HTTPFound(location=model_url(context, request))

    if 'form.submitted' in request.POST:
        try:
            converted = form.validate(request.POST)
            objectEventNotify(ObjectWillBeModifiedEvent(context))

            try:
                users.change_login(userid, converted['login'])
            except ValueError, e:
                raise CustomInvalid({'login': str(e)})

            for field in group_fields:
                group = field['group']
                fieldname = field['fieldname']
                if converted[fieldname]:
                    if group not in user_groups:
                        users.add_user_to_group(userid, group)
                else:
                    if group in user_groups:
                        users.remove_user_from_group(userid, group)

            if converted['password']:
                users.change_password(userid, converted['password'])

            # Handle simple fields
            for name in form.simple_field_names:
                setattr(context, name, converted.get(name))

            handle_photo_upload(context, converted, thumbnail=True)

            # Emit a modified event for recataloging
            objectEventNotify(ObjectModifiedEvent(context))

            path = model_url(context, request)
            msg = '?status_message=User%20edited'
            return HTTPFound(location=path+msg)

        except Invalid, e:
            fielderrors = e.error_dict
            fill_values = form.convert(request.POST)
            try:
                del fill_values['photo'] # filler cant handle photo field
            except KeyError:
                pass
    else:
        fielderrors = {}

        # pre-fill form with model values
        fill_values = form.from_python({})
        fill_values['login'] = user['login']

        for field in group_fields:
            group = field['group']
            fieldname = field['fieldname']
            fill_values[fieldname] = group in user_groups

    page_title = 'Edit ' + context.title
    api = TemplateAPI(context, request, page_title)

    # Display portrait
    photo = context.get_photo()
    display_photo = {}
    if photo is not None:
        display_photo["url"] = model_url(photo, request)
        display_photo["may_delete"] = True
    else:
        display_photo["url"] = api.static_url + "/images/defaultUser.gif"
        display_photo["may_delete"] = False

    return render_form_to_response(
        'templates/admin_edit_profile.pt',
        form,
        fill_values,
        post_url=request.url,
        formfields=api.formfields,
        fielderrors=fielderrors,
        api=api,
        photo=display_photo,
        group_fields=group_fields,
        )

class AdminEditProfileForm(EditProfileForm):
    login = baseforms.login
    home_path = baseforms.HomePath(strip=True)
    simple_field_names = EditProfileForm.simple_field_names + ['home_path']
    password = baseforms.PasswordChecker(strip=True)
    password_confirm = validators.UnicodeString(strip=True)
    chained_validators = baseforms.chained_validators

def get_profile_actions(profile, request):
    actions = []
    same_user = (authenticated_userid(request) == profile.__name__)
    if has_permission('administer', profile, request):
        actions.append(('Edit', 'admin_edit_profile.html'))
    elif same_user:
        actions.append(('Edit', 'edit_profile.html'))
    #if has_permission('delete', profile, request) and not same_user:
    #    actions.append(('Delete', 'delete.html'))
    if same_user:
        actions.append(('Manage Communities', 'manage_communities.html'))
        actions.append(('Manage Tags', 'manage_tags.html'))
    return actions

def show_profile_view(context, request):
    """Show a profile with actions if the current user"""
    page_title = 'View Profile'
    api = TemplateAPI(context, request, page_title)

    # Create display values from model object
    profile = {}
    for name in [name for name in context.__dict__.keys()
                 if not name.startswith("_")]:
        profile_value = getattr(context, name)
        if profile_value is not None:
            # Don't produce u'None'
            profile[name] = unicode(profile_value)
        else:
            profile[name] = None

    if profile.has_key("languages"):
        profile["languages"] = context.languages

    if profile.has_key("department"):
        profile["department"] = context.department

    if profile.has_key("country"):
        # translate from country code to country name
        country_code = profile["country"]
        country = countries.as_dict.get(country_code, u'')
        profile["country"] = country

    # Display portrait
    photo = context.get_photo()
    display_photo = {}
    if photo is not None:
        display_photo["url"] = model_url(photo, request)
    else:
        display_photo["url"] = api.static_url + "/images/defaultUser.gif"
    profile["photo"] = display_photo

    # provide client data for rendering current tags in the tagbox
    client_json_data = dict(
        tagbox = get_tags_client_data(context, request),
        )

    # Get communities this user is a member of, along with moderator info
    #
    communities = {}
    communities_folder = find_communities(context)
    user_info = find_users(context).get_by_id(context.__name__)
    if user_info is None:
        raise KeyError(context.__name__)

    for group in user_info["groups"]:
        if group.startswith("group.community:"):
            unused, community_name, role = group.split(":")
            if communities.has_key(community_name) and role != "moderators":
                continue

            community = communities_folder.get(community_name, None)
            if community is None:
                continue

            if has_permission('view', community, request):
                communities[community_name] = {
                    "title": community.title,
                    "moderator": role == "moderators",
                    "url": model_url(community, request),
                }

    communities = communities.values()
    communities.sort(key=lambda x:x["title"])

    tagger = find_tags(context)
    if tagger is None:
        tags = ()
    else:
        tags = []
        names = tagger.getTags(users=[context.__name__])
        for name, count in sorted(tagger.getFrequency(names,
                                                      user=context.__name__),
                                  key=lambda x: x[1],
                                  reverse=True,
                                 )[:10]:
            tags.append({'name': name, 'count': count})

    # List recently added content
    num, docids, resolver = ICatalogSearch(context)(
        sort_index='creation_date', reverse=True,
        interfaces=[IContent], limit=5, creator=context.__name__,
        allowed={'query': effective_principals(request), 'operator': 'or'},
        )
    recent_items = []
    for docid in docids:
        item = resolver(docid)
        if item is None:
            continue
        adapted = getMultiAdapter((item, request), IGridEntryInfo)
        recent_items.append(adapted)

    return render_template_to_response(
        'templates/profile.pt',
        api=api,
        profile=profile,
        actions=get_profile_actions(context, request),
        photo=photo,
        head_data=convert_to_script(client_json_data),
        communities=communities,
        tags=tags,
        recent_items=recent_items,
        )

def recent_content_view(context, request):
    batch = get_catalog_batch(context, request,
        sort_index='creation_date', reverse=True,
        interfaces=[IContent], creator=context.__name__,
        allowed={'query': effective_principals(request), 'operator': 'or'},
        )

    recent_items = []
    for item in batch['entries']:
        adapted = getMultiAdapter((item, request), IGridEntryInfo)
        recent_items.append(adapted)

    page_title = "Content Added Recently by %s" % context.title
    api = TemplateAPI(context, request, page_title)
    return render_template_to_response(
        'templates/profile_recent_content.pt',
        api=api,
        batch_info=batch,
        recent_items=recent_items,
        )

def may_leave(userid, community):
    # May not leave community if a moderator
    return userid not in community.moderator_names

    # Alternatively, may not leave community if *sole* moderator
    # may_leave = len(community.moderator_names) > 1 or \
    #           userid not in community.moderator_names

def manage_communities_view(context, request):
    assert IProfile.providedBy(context)

    page_title = 'Manage Communities'
    api = TemplateAPI(context, request, page_title)

    users = find_users(context)
    communities_folder = find_communities(context)
    userid = context.__name__

    # Handle cancel
    if request.params.get("form.cancel", False):
        return HTTPFound(location=model_url(context, request))

    # Handle form submission
    if request.params.get("form.submitted", False):
        for key in request.params:
            if key.startswith("leave_"):
                community_name = key[6:]
                community = communities_folder[community_name]

                # Not concerned about catching this exception, since checkbox
                # should not have been displayed in form unless user allowed
                # to leave.  Assert merely guards integrity of the system.
                assert may_leave(userid, community)

                if userid in community.moderator_names:
                    users.remove_group(userid, community.moderators_group_name)
                if userid in community.member_names:
                    users.remove_group(userid, community.members_group_name)

            elif key.startswith("alerts_pref_"):
                community_name = key[12:]
                preference = int(request.params.get(key))
                context.set_alerts_preference(community_name, preference)

        path = model_url(context, request)
        msg = '?status_message=Community+preferences+updated.'
        return HTTPFound(location=path+msg)

    # XXX Iterating over every community in the system isn't a particularly
    #     efficient solution.  Should use catalog.
    communities = []
    for community in communities_folder.values():
        if (userid in community.member_names or
            userid in community.moderator_names):
            alerts_pref = context.get_alerts_preference(community.__name__)
            display_community = {
                'name': community.__name__,
                'title': community.title,
                'alerts_pref': [
                    { "value": IProfile.ALERT_IMMEDIATELY,
                      "label": "Immediately",
                      "selected": alerts_pref == IProfile.ALERT_IMMEDIATELY,
                    },
                    { "value": IProfile.ALERT_DIGEST,
                      "label": "Digest",
                      "selected": alerts_pref == IProfile.ALERT_DIGEST,
                    },
                    { "value": IProfile.ALERT_NEVER,
                      "label": "Never",
                      "selected": alerts_pref == IProfile.ALERT_NEVER,
                    }],
                'may_leave': may_leave(userid, community),
            }
            communities.append(display_community)

    if len(communities) > 1:
        communities.sort(key=lambda x: x["title"])

    return render_template_to_response(
        'templates/manage_communities.pt',
        api=api,
        communities=communities,
        post_url=request.url,
        formfields=api.formfields,
    )

def show_profiles_view(context, request):

    page_title = 'KARL Profiles'
    api = TemplateAPI(context, request, page_title)

    # Grab the data for the two listings, main communities and portlet
    search = ICatalogSearch(context)

    query = dict(sort_index='title', interfaces=[IProfile], limit=5)

    titlestartswith = request.params.get('titlestartswith')
    if titlestartswith:
        query['titlestartswith'] = (titlestartswith, titlestartswith)

    num, docids, resolver = search(**query)

    profiles = []
    for docid in docids:
        model = resolver(docid)
        if model is None:
            continue
        profiles.append(model)

    mgr = ILetterManager(context)
    letter_info = mgr.get_info(request)

    return render_template_to_response(
        'templates/profiles.pt',
        api=api,
        profiles=profiles,
        letters=letter_info,
        )

def change_password_view(context, request):
    min_pw_length = get_setting(context, 'min_pw_length')
    form = ChangePasswordForm(min_pw_length=min_pw_length)
    if 'form.cancel' in request.POST:
        return HTTPFound(location=model_url(context, request))

    if 'form.submitted' in request.POST:
        try:
            converted = form.validate(request.POST)
            users = find_users(context)
            userid = context.__name__
            user = users.get_by_id(userid)

            # check the old password
            # XXX: repoze.who.plugins.zodb.interfaces.IUsers
            # really should have a check_password(id, password)
            # method.  We shouldn't have to use get_sha_password
            # directly.
            enc = get_sha_password(converted['old_password'])
            if enc != user['password']:
                raise CustomInvalid({'old_password': 'Incorrect password'})

            users.change_password(userid, converted['password'])

            # send email
            mail = email.message.Message()
            admin_email = get_setting(context, 'admin_email')
            mail["From"] = "KARL Administrator <%s>" % admin_email
            mail["To"] = "%s <%s>" % (context.title, context.email)
            mail["Subject"] = "KARL Password Change Notification"
            body = render_template(
                "templates/email_change_password.pt",
                login=user['login'],
                password=converted['password'],
            )

            if isinstance(body, unicode):
                body = body.encode("UTF-8")

            mail.set_payload(body, "UTF-8")
            mail.set_type("text/html")

            recipients = [context.email]
            mailer = getUtility(IMailDelivery)
            mailer.send(admin_email, recipients, mail.as_string())

            path = model_url(context, request)
            msg = '?status_message=Password%20changed'
            return HTTPFound(location=path+msg)

        except Invalid, e:
            fielderrors = e.error_dict
            fill_values = form.convert(request.POST)
    else:
        # fill_values not empty to work around chained validator
        # for password and password_confirm
        fill_values = {'password':'', 'password_confirm':''}
        fielderrors = {}

    page_title = 'Change Password'
    api = TemplateAPI(context, request, page_title)

    return render_form_to_response(
        'templates/change_password.pt',
        form,
        fill_values,
        post_url=request.url,
        formfields=api.formfields,
        fielderrors=fielderrors,
        api=api,
        )

class ChangePasswordForm(FormSchema):
    old_password = baseforms.old_password
    password = baseforms.password
    password_confirm = baseforms.password_confirm
    chained_validators = baseforms.chained_validators

def delete_profile_view(context, request):

    confirm = request.params.get('confirm')
    if confirm:
        parent = context.__parent__
        name = context.__name__
        find_users(context).remove(name)
        del parent[name]

        if authenticated_userid(request) == name:
            return logout_view(context, request, reason='User removed')
        query = {'status_message': 'Deleted profile: %s' % name}
        location = model_url(parent, request, query=query)

        return HTTPFound(location=location)

    page_title = 'Delete Profile for %s %s' % (context.firstname,
                                               context.lastname)
    api = TemplateAPI(context, request, page_title)

    # Get a layout
    return render_template_to_response(
        'templates/delete_profile.pt',
        api=api,
        )

def add_user_view(context, request):
    min_pw_length = get_setting(context, 'min_pw_length')
    form = AddUserForm(context=context, min_pw_length=min_pw_length)
    group_fields = get_group_fields(context)
    for field in group_fields:
        validator = validators.Bool(if_missing=False, default=False)
        form.add_field(field['fieldname'], validator)

    if 'form.cancel' in request.POST:
        return HTTPFound(location=model_url(context, request))

    if 'form.submitted' in request.POST:
        try:
            converted = form.validate(request.POST)
            userid = converted['login']
            users = find_users(context)
            if users.get_by_id(userid) is not None or userid in context:
                raise CustomInvalid(
                    {'login': "User ID '%s' already exists" % userid})

            groups = []
            for field in group_fields:
                fieldname = field['fieldname']
                if converted[fieldname]:
                    groups.append(field['group'])

            users.add(userid, userid, converted['password'], groups)

            kw = {}
            for k, v in converted.items():
                if k in ('login', 'password', 'password_confirm',
                        'photo', 'photo_delete'):
                    continue
                if k.startswith('groupfield-'):
                    continue
                kw[k] = v
            profile = create_content(IProfile, **kw)

            context[userid] = profile

            # Set up workflow
            security_adapter = ISecurityWorkflow(profile)
            security_adapter.setInitialState(request, **converted)

            handle_photo_upload(profile, converted, thumbnail=True)

            location = model_url(profile, request)
            return HTTPFound(location=location)

        except Invalid, e:
            fielderrors = e.error_dict
            fill_values = form.convert(request.POST)
            try:
                del fill_values['photo'] # rendering cant deal with photo
            except KeyError:
                pass
    else:
        fielderrors = {}
        fill_values = {}

    page_title = 'Add User'
    api = TemplateAPI(context, request, page_title)

    return render_form_to_response(
        'templates/add_user.pt',
        form,
        fill_values,
        post_url=request.url,
        formfields=api.formfields,
        fielderrors=fielderrors,
        group_fields=group_fields,
        api=api,
        )

class AddUserForm(EditProfileForm):
    login = baseforms.login
    home_path = validators.UnicodeString(strip=True)
    simple_field_names = EditProfileForm.simple_field_names + ['home_path']
    password = baseforms.password
    password_confirm = baseforms.password_confirm
    chained_validators = baseforms.chained_validators
