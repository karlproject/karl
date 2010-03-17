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

import karl.mail
import formish
import schemaish
from schemaish.type import File as SchemaFile
from validatish import validator

from formencode import Invalid
from repoze.bfg.chameleon_zpt import render_template
from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.formish import ValidationError
from repoze.bfg.security import authenticated_userid
from repoze.bfg.security import effective_principals
from repoze.bfg.security import has_permission
from repoze.bfg.url import model_url
from repoze.workflow import get_workflow
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
from karl.utils import find_communities
from karl.utils import find_tags
from karl.utils import find_users
from karl.utils import get_layout_provider
from karl.utils import get_setting
from karl.views import baseforms
from karl.views.api import TemplateAPI
from karl.views.batch import get_catalog_batch
from karl.views.login import logout_view
from karl.views.tags import get_tags_client_data
from karl.views.utils import convert_to_script
from karl.views.utils import CustomInvalid
from karl.views.utils import handle_photo_upload
from karl.views.utils import photo_from_filestore_view
from karl.views.form import render_form_to_response
from karl.views.forms import widgets as karlwidgets
from karl.views.forms import validators as karlvalidators
from karl.views.forms.filestore import get_filestore


def edit_profile_filestore_photo_view(context, request):
    return photo_from_filestore_view(context, request, 'edit-profile')

def add_user_filestore_photo_view(context, request):
    return photo_from_filestore_view(context, request, 'add-user')

firstname_field = schemaish.String(validator=validator.Required(),
                                   title='First Name')
lastname_field = schemaish.String(validator=validator.Required(),
                                  title='Last Name')
phone_field = schemaish.String(title='Phone Number')
extension_field = schemaish.String()
department_field = schemaish.String()
position_field = schemaish.String()
organization_field = schemaish.String()
location_field = schemaish.String()
country_field = schemaish.String()
website_field = schemaish.String(validator=validator.Any(validator.URL(),
                                                         validator.Equal('')))
languages_field = schemaish.String()
photo_field = schemaish.File()
biography_field = schemaish.String()

class EditProfileFormController(object):
    """
    Formish controller for the profile edit form.  Also the base class
    for the controllers for the admin profile edit and add user forms.
    """
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

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.filestore = get_filestore(context, request, 'edit-profile')
        page_title = "Edit %s" % context.title
        self.api = TemplateAPI(context, request, page_title)
        photo = context.get_photo()
        if photo is not None:
            photo = SchemaFile(None, photo.__name__, photo.mimetype)
        self.photo = photo

    def form_fields(self):
        email_field = schemaish.String(
            validator=validator.All(validator.Required(),
                                    validator.Email(),
                                    karlvalidators.UniqueEmail(self.context)))
        fields = [('firstname', firstname_field),
                  ('lastname', lastname_field),
                  ('email', email_field),
                  ('phone', phone_field),
                  ('extension', extension_field),
                  ('department', department_field),
                  ('position', position_field),
                  ('organization', organization_field),
                  ('location', location_field),
                  ('country', country_field),
                  ('website', website_field),
                  ('languages', languages_field),
                  ('biography', biography_field),
                  ('photo', photo_field)]
        return fields

    def form_widgets(self, fields):
        default_icon = '%s/images/defaultUser.gif' % self.api.static_url
        show_remove_checkbox = self.photo is not None
        widgets = {'firstname': formish.Input(empty=''),
                   'lastname': formish.Input(empty=''),
                   'email': formish.Input(),
                   'phone': formish.Input(empty=''),
                   'extension': formish.Input(empty=''),
                   'department': formish.Input(empty=''),
                   'position': formish.Input(empty=''),
                   'organization': formish.Input(empty=''),
                   'location': formish.Input(empty=''),
                   'country': formish.SelectChoice(options=countries),
                   'website': formish.Input(empty=''),
                   'languages': formish.Input(empty=''),
                   'photo': karlwidgets.PhotoImageWidget(
                       filestore=self.filestore,
                       url_base=model_url(self.context, self.request),
                       image_thumbnail_default=default_icon,
                       show_remove_checkbox=show_remove_checkbox),
                   'biography': karlwidgets.RichTextWidget(empty=''),
                   }
        return widgets

    def form_defaults(self):
        context = self.context
        defaults = {'firstname': context.firstname,
                    'lastname': context.lastname,
                    'email': context.email,
                    'phone': context.phone,
                    'extension': context.extension,
                    'department': context.department,
                    'position': context.position,
                    'organization': context.organization,
                    'location': context.location,
                    'country': context.country,
                    'website': context.website,
                    'languages': context.languages,
                    'photo': self.photo,
                    'biography': context.biography,
                    }
        return defaults

    def __call__(self):
        api = self.api
        layout_provider = get_layout_provider(self.context, self.request)
        layout = layout_provider('generic')
        if api.user_is_staff:
            self.request.form.edge_div_class = 'k3_staff_role'
        else:
            self.request.form.edge_div_class = 'k3_nonstaff_role'
        form_title = 'Edit Profile'
        return {'api':api, 'actions':(), 'layout':layout,
                'form_title': form_title, 'include_blurb': True}

    def handle_cancel(self):
        return HTTPFound(location=model_url(self.context, self.request))

    def handle_submit(self, converted):
        context = self.context
        request = self.request
        objectEventNotify(ObjectWillBeModifiedEvent(context))
        # Handle the easy ones
        for name in self.simple_field_names:
            setattr(context, name, converted.get(name))
        # Handle the picture and clear the temporary filestore
        handle_photo_upload(context, converted, thumbnail=True)
        self.filestore.clear()
        # Emit a modified event for recataloging
        objectEventNotify(ObjectModifiedEvent(context))
        # Whew, we made it!
        path = model_url(context, request)
        msg = '?status_message=Profile%20edited'
        return HTTPFound(location=path+msg)

login_field = schemaish.String(validator=validator.Required())
groups_field = schemaish.Sequence(schemaish.String(),
                                  title='Group Memberships')

class AdminEditProfileFormController(EditProfileFormController):
    """
    Extends the default profile edit controller w/ all of the extra
    logic that the admin form requires.
    """
    simple_field_names = EditProfileFormController.simple_field_names
    simple_field_names += ['home_path']

    def __init__(self, context, request):
        super(AdminEditProfileFormController, self).__init__(context, request)
        self.users = find_users(context)
        self.userid = context.__name__
        self.user = self.users.get_by_id(self.userid)
        self.user_groups = set(self.user['groups'])
        self.group_options = get_group_options(self.context)

    def form_fields(self):
        context = self.context
        min_pw_length = get_setting(context, 'min_pw_length')
        home_path_field = schemaish.String(
            validator=karlvalidators.PathExists(context),
            description=('The first page to show after logging in. '
                         'Leave blank to show a community or the '
                         'community list.'))
        password_field = schemaish.String(
            validator=karlvalidators.PasswordChecker(min_pw_length),
            title='Reset Password',
            description=('Enter a new password for the user here, '
                         'or leave blank to leave the password '
                         'unchanged.'))
        fields = [('login', login_field),
                  ('groups', groups_field),
                  ('home_path', home_path_field),
                  ('password', password_field)]
        fields += super(AdminEditProfileFormController, self).form_fields()
        return fields

    def form_widgets(self, fields):
        widgets = super(AdminEditProfileFormController, self).form_widgets(fields)
        groups_widget = formish.CheckboxMultiChoice(self.group_options)
        widgets.update({'login': formish.Input(empty=''),
                        'groups': groups_widget,
                        'home_path': formish.Input(empty=''),
                        'password': karlwidgets.KarlCheckedPassword()})
        return widgets

    def form_defaults(self):
        defaults = super(AdminEditProfileFormController, self).form_defaults()
        context = self.context
        defaults.update({'login': self.user['login'],
                         'groups': self.user_groups,
                         'home_path': context.home_path,
                         'password': ''})
        return defaults

    def __call__(self):
        api = self.api
        layout_provider = get_layout_provider(self.context, self.request)
        layout = layout_provider('generic')
        self.request.form.edge_div_class = 'k3_admin_role'
        form_title = 'Edit User and Profile Information'
        return {'api':api, 'actions':(), 'layout':layout,
                'form_title': form_title, 'include_blurb': False,
                'admin_edit': True}

    def handle_submit(self, converted):
        context = self.context
        request = self.request
        users = self.users
        userid = self.userid
        user = users.get_by_id(userid)
        login = converted.get('login')
        login_changed = users.get_by_login(login) != user
        if (login_changed and
            (users.get_by_id(login) is not None or
             users.get_by_login(login) is not None or
             login in context)):
            msg = "Login '%s' is already in use" % login
            raise ValidationError(login=msg)
        objectEventNotify(ObjectWillBeModifiedEvent(context))
        # Set new login
        try:
            users.change_login(userid, converted['login'])
        except ValueError, e:
            raise ValidationError(login=str(e))
        # Set group memberships
        user_groups = self.user_groups
        chosen_groups = set(converted['groups'])
        if user_groups != chosen_groups:
            for group in chosen_groups.difference(user_groups):
                users.add_user_to_group(userid, group)
            for group in user_groups.difference(chosen_groups):
                users.remove_user_from_group(userid, group)
        # Edit password
        if converted.get('password', None):
            users.change_password(userid, converted['password'])
        # Handle the easy ones
        for name in self.simple_field_names:
            setattr(context, name, converted.get(name))
        # Handle the picture and clear the temporary filestore
        handle_photo_upload(context, converted, thumbnail=True)
        self.filestore.clear()
        # Emit a modified event for recataloging
        objectEventNotify(ObjectModifiedEvent(context))
        # Whew, we made it!
        path = model_url(context, request)
        msg = '?status_message=User%20edited'
        return HTTPFound(location=path+msg)

def get_group_options(context):
    group_options = []
    for group in get_setting(context, "selectable_groups").split():
        if group.startswith('group.'):
            title = group[6:]
        else:
            title = group
        group_options.append((group, title))
    return group_options    

class AddUserFormController(EditProfileFormController):
    """
    Very similar to the AdminEditProfileFormController, but with just
    enough difference to make it more sane to not try to reuse it, so
    they both inherit from the same base.
    """
    simple_field_names = EditProfileFormController.simple_field_names
    simple_field_names += ['home_path']

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.filestore = get_filestore(context, request, 'add-user')
        page_title = 'Add User'
        self.api = TemplateAPI(context, request, page_title)
        self.photo = None
        self.users = find_users(context)
        self.group_options = get_group_options(self.context)

    def form_fields(self):
        context = self.context
        min_pw_length = get_setting(context, 'min_pw_length')
        home_path_field = schemaish.String(
            validator=karlvalidators.PathExists(context),
            description=('The first page to show after logging in. '
                         'Leave blank to show a community or the '
                         'community list.'))
        password_field = schemaish.String(
            validator=(validator.All(
                karlvalidators.PasswordChecker(min_pw_length),
                validator.Required())))
        fields = [('login', login_field),
                  ('groups', groups_field),
                  ('home_path', home_path_field),
                  ('password', password_field)]
        fields += super(AddUserFormController, self).form_fields()
        return fields

    def form_widgets(self, fields):
        widgets = super(AddUserFormController, self).form_widgets(fields)
        groups_widget = formish.CheckboxMultiChoice(self.group_options)
        widgets.update({'login': formish.Input(empty=''),
                        'groups': groups_widget,
                        'home_path': formish.Input(empty=''),
                        'password': karlwidgets.KarlCheckedPassword()})
        return widgets

    def form_defaults(self):
        return

    def __call__(self):
        api = self.api
        layout_provider = get_layout_provider(self.context, self.request)
        layout = layout_provider('generic')
        self.request.form.edge_div_class = 'k3_admin_role'
        form_title = 'Add User'
        return {'api':api, 'actions':(), 'layout':layout,
                'form_title': form_title, 'include_blurb': False}

    def handle_submit(self, converted):
        context = self.context
        request = self.request
        userid = converted['login']
        users = self.users
        if (users.get_by_id(userid) is not None or
            users.get_by_login(userid) is not None or
            userid in context):
            msg = "User ID '%s' is already in use" % userid
            raise ValidationError(login=msg)
        users.add(userid, userid, converted['password'], converted['groups'])

        kw = {}
        for k, v in converted.items():
            if k in ('login', 'password', 'password_confirm',
                     'photo', 'groups'):
                continue
            kw[k] = v
        profile = create_content(IProfile, **kw)
        context[userid] = profile

        workflow = get_workflow(IProfile, 'security', context)
        if workflow is not None:
            workflow.initialize(profile)

        handle_photo_upload(profile, converted, thumbnail=True)
        location = model_url(profile, request)
        return HTTPFound(location=location)

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
    if user_info is not None:
        for group in user_info["groups"]:
            if group.startswith("group.community:"):
                unused, community_name, role = group.split(":")
                if (communities.has_key(community_name) and
                    role != "moderators"):
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

        context.alert_attachments = request.params.get('attachments', 'link')

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
        attachments=context.alert_attachments,
    )

def show_profiles_view(context, request):
    system_name = get_setting(context, 'system_name', 'KARL')
    page_title = '%s Profiles' % system_name
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
            system_name = get_setting(context, 'system_name', 'KARL')
            mail = karl.mail.Message()
            admin_email = get_setting(context, 'admin_email')
            mail["From"] = "%s Administrator <%s>" % (system_name, admin_email)
            mail["To"] = "%s <%s>" % (context.title, context.email)
            mail["Subject"] = "%s Password Change Notification" % system_name
            system_name = get_setting(context, 'system_name', 'KARL')
            body = render_template(
                "templates/email_change_password.pt",
                login=user['login'],
                password=converted['password'],
                system_name=system_name,
            )

            if isinstance(body, unicode):
                body = body.encode("UTF-8")

            mail.set_payload(body, "UTF-8")
            mail.set_type("text/html")

            recipients = [context.email]
            mailer = getUtility(IMailDelivery)
            mailer.send(admin_email, recipients, mail)

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
