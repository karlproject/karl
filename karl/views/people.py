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

import uuid
from datetime import datetime
from datetime import timedelta
import hashlib

import formish
from pyramid.renderers import get_renderer
from pyramid.renderers import render_to_response
from pyramid_formish import ValidationError
from pyramid.security import authenticated_userid
from pyramid.security import effective_principals
from pyramid.security import has_permission
from pyramid.url import resource_url
from repoze.lemonade.content import create_content
from repoze.lemonade.interfaces import IContent
from repoze.workflow import get_workflow
import schemaish
from schemaish.type import File as SchemaFile
import validatish
from validatish import validator
from persistent.list import PersistentList
from pyramid.httpexceptions import HTTPFound
from pyramid.exceptions import Forbidden
from repoze.who.plugins.zodb.users import get_sha_password
from zope.component.event import objectEventNotify
from zope.component import getMultiAdapter

from karl.consts import countries
from karl.consts import cultures
from karl.events import ObjectModifiedEvent
from karl.events import ObjectWillBeModifiedEvent
import karl.models.interfaces
from karl.models.interfaces import ICatalogSearch
from karl.models.interfaces import IGridEntryInfo
from karl.models.interfaces import IInvitation
from karl.models.interfaces import ILetterManager
from karl.models.interfaces import IProfile
from karl.utilities.image import thumb_url
from karl.utils import find_communities
from karl.utils import find_peopledirectory
from karl.utils import find_tags
from karl.utils import find_users
from karl.utils import get_layout_provider
from karl.utils import get_setting
from karl.views.api import TemplateAPI
from karl.views.api import xhtml
from karl.views.batch import get_catalog_batch
from karl.views.login import logout_view
from karl.views.resetpassword import request_password_reset
from karl.views.tags import get_tags_client_data
from karl.views.utils import Invalid
from karl.views.utils import convert_to_script
from karl.views.utils import handle_photo_upload
from karl.views.utils import photo_from_filestore_view
from karl.views.forms import widgets as karlwidgets
from karl.views.forms import validators as karlvalidators
from karl.views.forms.filestore import get_filestore
from karl.views.communities import get_preferred_communities
from karl.views.communities import get_my_communities

PROFILE_THUMB_SIZE = (75, 100)

_MIN_PW_LENGTH = None

def min_pw_length():
    global _MIN_PW_LENGTH
    if _MIN_PW_LENGTH is None:
        _MIN_PW_LENGTH = get_setting(None, 'min_pw_length', 8)
    return _MIN_PW_LENGTH

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
fax_field = schemaish.String(title='Fax Number')
department_field = schemaish.String()
position_field = schemaish.String()
organization_field = schemaish.String()
location_field = schemaish.String()
country_field = schemaish.String(validator=validator.Required())
websites_field = schemaish.Sequence(
                    schemaish.String(validator=karlvalidators.WebURL()))
languages_field = schemaish.String()
photo_field = schemaish.File()
biography_field = schemaish.String()
date_format_field = schemaish.String(title='Preferred Date Format')

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
        "fax",
        "department",
        "position",
        "organization",
        "location",
        "country",
        "websites",
        "languages",
        "office",
        "room_no",
        "biography",
        "date_format",
    ]

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.filestore = get_filestore(context, request, 'edit-profile')
        self.page_title = "Edit %s" % context.title
        photo = context.get('photo')
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
                  ('fax', fax_field),
                  ('department', department_field),
                  ('position', position_field),
                  ('organization', organization_field),
                  ('location', location_field),
                  ('country', country_field),
                  ('websites', websites_field),
                  ('languages', languages_field),
                  ('biography', biography_field),
                  ('photo', photo_field),
                  ('date_format', date_format_field)]
        return fields

    def form_widgets(self, fields):
        api = TemplateAPI(self.context, self.request, self.page_title)
        default_icon = '%s/images/defaultUser.gif' % api.static_url
        show_remove_checkbox = self.photo is not None
        widgets = {'firstname': formish.Input(empty=''),
                   'lastname': formish.Input(empty=''),
                   'email': formish.Input(),
                   'phone': formish.Input(empty=''),
                   'extension': formish.Input(empty=''),
                   'fax': formish.Input(empty=''),
                   'department': formish.Input(empty=''),
                   'position': formish.Input(empty=''),
                   'organization': formish.Input(empty=''),
                   'location': formish.Input(empty=''),
                   'country': formish.SelectChoice(options=countries),
                   'websites': formish.TextArea(
                            rows=3,
                            converter_options={'delimiter':'\n'}),
                   'languages': formish.Input(empty=''),
                   'photo': karlwidgets.PhotoImageWidget(
                       filestore=self.filestore,
                       url_base=resource_url(self.context, self.request),
                       image_thumbnail_default=default_icon,
                       show_remove_checkbox=show_remove_checkbox),
                   'biography': karlwidgets.RichTextWidget(empty=''),
                   'date_format': karlwidgets.VerticalRadioChoice(
                       options=cultures,
                       none_option=None),
                   }
        return widgets

    def form_defaults(self):
        context = self.context
        defaults = {'firstname': context.firstname,
                    'lastname': context.lastname,
                    'email': context.email,
                    'phone': context.phone,
                    'extension': context.extension,
                    'fax': context.fax,
                    'department': context.department,
                    'position': context.position,
                    'organization': context.organization,
                    'location': context.location,
                    'country': context.country,
                    'websites': context.websites,
                    'languages': context.languages,
                    'photo': self.photo,
                    'biography': context.biography,
                    'date_format': context.date_format,
                    }
        return defaults

    def __call__(self):
        _fix_website_validation_errors(self.request.form)
        api = TemplateAPI(self.context, self.request, self.page_title)
        if api.user_is_admin:
            return HTTPFound(location=resource_url(self.context,
                self.request, 'admin_edit_profile.html'))
        layout_provider = get_layout_provider(self.context, self.request)
        layout = layout_provider('generic')
        if api.user_is_staff:
            self.request.form.edge_div_class = 'k3_staff_role'
        else:
            self.request.form.edge_div_class = 'k3_nonstaff_role'
        form_title = 'Edit Profile'
        same_user = authenticated_userid(self.request) == self.context.__name__
        return {'api':api, 'actions':(), 'layout':layout,
                'same_user': same_user, 'form_title': form_title,
                'include_blurb': True}

    def handle_cancel(self):
        return HTTPFound(location=resource_url(self.context, self.request))

    def handle_submit(self, converted):
        context = self.context
        request = self.request
        objectEventNotify(ObjectWillBeModifiedEvent(context))
        _normalize_websites(converted)
        # Handle the easy ones
        for name in self.simple_field_names:
            setattr(context, name, converted.get(name))
        # Handle the picture and clear the temporary filestore
        try:
            handle_photo_upload(context, converted)
        except Invalid, e:
            raise ValidationError(**e.error_dict)
        self.filestore.clear()
        context.modified_by = authenticated_userid(request)
        # Emit a modified event for recataloging
        objectEventNotify(ObjectModifiedEvent(context))
        # Whew, we made it!
        path = resource_url(context, request)
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
    simple_field_names = simple_field_names + ['home_path']

    def __init__(self, context, request):
        super(AdminEditProfileFormController, self).__init__(context, request)
        self.users = find_users(context)
        self.userid = context.__name__
        self.user = self.users.get_by_id(self.userid)
        if self.user is not None:
            self.is_active = True
            self.user_groups = set(self.user['groups'])
            self.group_options = get_group_options(self.context)
        else:
            self.is_active = False

    def form_fields(self):
        context = self.context
        home_path_field = schemaish.String(
            validator=karlvalidators.PathExists(context),
            description=('The first page to show after logging in. '
                         'Leave blank to show a community or the '
                         'community list.'))
        if self.user is not None:
            password_field = schemaish.String(
                validator=karlvalidators.PasswordLength(min_pw_length()),
                title='Reset Password',
                description=('Enter a new password for the user here, '
                             'or leave blank to leave the password '
                             'unchanged.'))
            fields = [('login', login_field),
                      ('groups', groups_field),
                      ('home_path', home_path_field),
                      ('password', password_field)]
        else:
            fields = [('home_path', home_path_field)]
        fields += super(AdminEditProfileFormController, self).form_fields()
        return fields

    def form_widgets(self, fields):
        widgets = super(AdminEditProfileFormController, self
                       ).form_widgets(fields)
        if self.user is not None:
            groups_widget = formish.CheckboxMultiChoice(self.group_options)
            widgets.update({'login': formish.Input(empty=''),
                            'groups': groups_widget,
                            'password': karlwidgets.KarlCheckedPassword(),
                           })
        widgets.update({'home_path': formish.Input(empty=''),
                        'websites': formish.TextArea(
                            rows=3,
                            converter_options={'delimiter':'\n'}),
                       })
        return widgets

    def form_defaults(self):
        defaults = super(AdminEditProfileFormController, self).form_defaults()
        context = self.context
        if self.user is not None:
            defaults.update({'login': self.user['login'],
                             'groups': self.user_groups,
                             'password': ''})
        defaults['home_path'] = context.home_path
        return defaults

    def __call__(self):
        _fix_website_validation_errors(self.request.form)
        api = TemplateAPI(self.context, self.request, self.page_title)
        layout_provider = get_layout_provider(self.context, self.request)
        layout = layout_provider('generic')
        self.request.form.edge_div_class = 'k3_admin_role'
        form_title = 'Edit User and Profile Information'
        return {'api':api, 'actions':(), 'layout':layout,
                'form_title': form_title, 'include_blurb': False,
                'admin_edit': True, 'is_active': self.is_active}

    def handle_submit(self, converted):
        context = self.context
        request = self.request
        users = self.users
        userid = self.userid
        user = self.user
        if user is not None:
            login = converted.get('login')
            login_changed = users.get_by_login(login) != user
            if (login_changed and
                (users.get_by_id(login) is not None or
                 users.get_by_login(login) is not None or
                 login in context)):
                msg = "Login '%s' is already in use" % login
                raise ValidationError(login=msg)
        objectEventNotify(ObjectWillBeModifiedEvent(context))
        if user is not None:
            # Set new login
            try:
                users.change_login(userid, converted['login'])
            except ValueError, e:
                raise ValidationError(login=str(e))
            # Set group memberships
            user_groups = self.user_groups
            chosen_groups = set(converted['groups'])
            for group, group_title in self.group_options:
                if group in chosen_groups and group not in user_groups:
                    users.add_user_to_group(userid, group)
                if group in user_groups and group not in chosen_groups:
                    users.remove_user_from_group(userid, group)
            # Edit password
            if converted.get('password', None):
                new_password = converted['password']
                sha_password = get_sha_password(new_password)
                if context.last_passwords is None:
                    context.last_passwords = PersistentList()
                if sha_password in context.last_passwords:
                    msg = "Please use a password that was not previously used"
                    raise ValidationError(password=msg)
                users.change_password(userid, new_password)
                context.last_passwords.append(sha_password)
                if len(context.last_passwords) > 10:
                    context.last_passwords = context.last_passwords[1:]
                self.request.session['password_expired'] = False
                context.password_expiration_date = (datetime.utcnow()
                                                    + timedelta(days=180))
        _normalize_websites(converted)
        # Handle the easy ones
        for name in self.simple_field_names:
            setattr(context, name, converted.get(name))
        # Handle the picture and clear the temporary filestore
        try:
            handle_photo_upload(context, converted)
        except Invalid, e:
            raise ValidationError(**e.error_dict)
        self.filestore.clear()
        context.modified_by = authenticated_userid(request)
        # Emit a modified event for recataloging
        objectEventNotify(ObjectModifiedEvent(context))
        # Whew, we made it!
        path = resource_url(context, request)
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
    reactivate_user = None
    simple_field_names = EditProfileFormController.simple_field_names
    simple_field_names = simple_field_names + ['home_path']

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.filestore = get_filestore(context, request, 'add-user')
        self.photo = None
        self.users = find_users(context)
        self.group_options = get_group_options(self.context)
        self.page_title = 'Add User'

    def form_fields(self):
        context = self.context
        home_path_field = schemaish.String(
            validator=karlvalidators.PathExists(context),
            description=('The first page to show after logging in. '
                         'Leave blank to show a community or the '
                         'community list.'))
        password_field = schemaish.String(
            validator=(validator.All(
                karlvalidators.PasswordLength(min_pw_length()),
                validator.Required())))
        fields = [('login', login_field),
                  ('groups', groups_field),
                  ('home_path', home_path_field),
                  ('password', password_field)]
        fields += super(AddUserFormController, self).form_fields()

        # Get rid of unique email address validation, because we need to do
        # that in the controller so we can manage whether or not email belongs
        # to deactivated user.
        email_field = schemaish.String(
            validator=validator.All(validator.Required(),
                                    validator.Email()))
        for i in xrange(len(fields)):
            if fields[i][0] == 'email':
                fields[i] = ('email', email_field)
                break

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
        _fix_website_validation_errors(self.request.form)
        api = TemplateAPI(self.context, self.request, self.page_title)
        layout_provider = get_layout_provider(self.context, self.request)
        layout = layout_provider('generic')
        self.request.form.edge_div_class = 'k3_admin_role'
        form_title = 'Add User'
        return {'api':api, 'actions':(), 'layout':layout,
                'form_title': form_title, 'include_blurb': False,
                'reactivate_user': self.reactivate_user}

    def handle_submit(self, converted):
        context = self.context
        request = self.request
        userid = converted['login']
        users = self.users
        if (users.get_by_id(userid) is not None or
            users.get_by_login(userid) is not None):
            msg = "User ID '%s' is already in use" % userid
            raise ValidationError(login=msg)
        profile = context.get(userid)
        if profile is not None:
            if profile.security_state == 'inactive':
                url = resource_url(profile, request, 'reactivate.html')
                self.reactivate_user = dict(userid=userid, url=url)
                msg = ("User ID '%s' is used by a previously deactivated "
                       "user.  Perhaps you mean to reactivate this user. "
                       "See link above."%
                       userid)
            else:
                msg = "User ID '%s' is already in use" % userid
            raise ValidationError(login=msg)

        search = ICatalogSearch(context)
        count, docids, resolver = search(
            interfaces=[IProfile], email=converted['email']
        )
        if count:
            msg = 'Email address is already in use by another user(s).'
            if count == 1:
                profile = resolver(docids[0])
                if profile.security_state ==  'inactive':
                    url = resource_url(profile, request, 'reactivate.html')
                    userid = profile.__name__
                    self.reactivate_user = dict(userid=userid, url=url)
                    msg = ("Email address is in use by a previously "
                           "deactivated user.  Perhaps you mean to reactivate "
                           "this user. See link above.")
            raise ValidationError(email=msg)

        # If user was previously invited to join any communities, those
        # invitations are no longer needed.
        count, docids, resolver = search(
            interfaces=[IInvitation], email=converted['email'])
        for docid in docids:
            invitation = resolver(docid)
            del invitation.__parent__[invitation.__name__]

        users.add(userid, userid, converted['password'], converted['groups'])

        _normalize_websites(converted)
        kw = {}
        for k, v in converted.items():
            if k in ('login', 'password', 'password_confirm',
                     'photo', 'groups'):
                continue
            kw[k] = v
        profile = create_content(IProfile, **kw)
        profile.modified_by = authenticated_userid(request)

        password = get_sha_password(converted['password'])
        profile.last_passwords = PersistentList([password])

        context[userid] = profile

        workflow = get_workflow(IProfile, 'security', context)
        if workflow is not None:
            workflow.initialize(profile)

        try:
            handle_photo_upload(profile, converted)
        except Invalid, e:
            raise ValidationError(**e.error_dict)
        location = resource_url(profile, request)
        return HTTPFound(location=location)

def _normalize_websites(converted):
    websites = converted.setdefault('websites', [])
    if websites is None:
        # Work around formish / schemaish passing None
        websites = converted['websites'] = []
    # prepend http:// to the website URL if necessary
    for i, website in enumerate(websites):
        if website.startswith('www.'):
            websites[i] = 'http://%s' % website

def _fix_website_validation_errors(form):
    # The websites field is a sequence but it uses a textarea widget, which
    # seems to confuse formish, because it's assuming you're using that widget
    # for a scalar.  (At least that's my best theory so far.)  As a work around,
    # go fishing in the form errors for website errors and move them up to the
    # level of the entire field rather than the level of a particular value.
    if 'websites' in form.errors:
        # Refuse to clobber a field level error message if one is set
        return

    errors = []
    for name in list(form.errors):
        if name.startswith('websites.'):
            error = form.errors[name]
            errors.append(str(error))
            del form.errors[name]
    if errors:
        form.errors['websites'] = validatish.Invalid('\n'.join(errors))

def get_profile_actions(profile, request):
    profile_url = request.resource_url(profile)
    actions = []
    same_user = (authenticated_userid(request) == profile.__name__)
    if has_permission('administer', profile, request):
        actions.append(('Edit', '%sadmin_edit_profile.html' % profile_url))
    elif same_user:
        actions.append(('Edit', '%sedit_profile.html' % profile_url))
    if same_user:
        actions.append(('Manage Communities', 'manage_communities.html'))
        actions.append(('Manage Tags', 'manage_tags.html'))
    if has_permission('administer', profile, request):
        actions.append(('Advanced', '%sadvanced.html' % profile_url))
    return actions

def show_profile_view(context, request):
    """Show a profile with actions if the current user"""
    page_title = "Profile: %s" % context.title
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

    if 'fax' not in profile:
        profile['fax'] = '' # BBB

    # 'websites' is a property, so the loop above misses it
    profile["websites"] = context.websites

    # ditto for 'title'
    profile["title"] = context.title

    if profile.has_key("languages"):
        profile["languages"] = context.languages

    if profile.has_key("department"):
        profile["department"] = context.department

    if profile.get("last_login_time"):
        stamp = context.last_login_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        profile["last_login_time"] = stamp

    if profile.has_key("country"):
        # translate from country code to country name
        country_code = profile["country"]
        country = countries.as_dict.get(country_code, u'')
        profile["country"] = country

    # Display portrait
    photo = context.get('photo')
    display_photo = {}
    if photo is not None:
        display_photo["url"] = thumb_url(photo, request, PROFILE_THUMB_SIZE)
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
                        "url": resource_url(community, request),
                    }

    communities = communities.values()
    communities.sort(key=lambda x:x["title"])

    preferred_communities = []
    my_communities = None
    name = context.__name__
    # is this the current user's profile?
    if authenticated_userid(request) == name:
        preferred_communities = get_preferred_communities(communities_folder,
                                                          request)
        my_communities = get_my_communities(communities_folder, request)

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
    _, items, _ = karl.models.interfaces.ISQLCatalogSearch(context)(
        sort_index='creation_date', reverse=True,
        interfaces=[IContent], limit=5, creator=context.__name__,
        allowed={'query': effective_principals(request), 'operator': 'or'},
        want_count=False,
        )
    recent_items = []
    for item in items:
        adapted = getMultiAdapter((item, request), IGridEntryInfo)
        recent_items.append(adapted)

    recent_url = request.resource_url(context, 'recent_content.html')

    return dict(api=api,
        profile=profile,
        actions=get_profile_actions(context, request),
        photo=photo,
        head_data=convert_to_script(client_json_data),
        communities=communities,
        my_communities=my_communities,
        preferred_communities=preferred_communities,
        tags=tags,
        recent_items=recent_items,
        recent_url=recent_url)

def profile_thumbnail(context, request):
    api = TemplateAPI(context, request, 'Profile thumbnail redirector')
    photo = context.get('photo')
    if photo is not None:
        url = thumb_url(photo, request, PROFILE_THUMB_SIZE)
    else:
        url = api.static_url + "/images/defaultUser.gif"
    return HTTPFound(location=url)

def recent_content_view(context, request):
    batch = get_catalog_batch(
        context, request,
        sort_index='creation_date', reverse=True,
        interfaces=[IContent], creator=context.__name__,
        allowed={'query': effective_principals(request), 'operator': 'or'},
        catalog_iface=karl.models.interfaces.ISQLCatalogSearch,
        )

    recent_items = []
    for item in batch['entries']:
        adapted = getMultiAdapter((item, request), IGridEntryInfo)
        recent_items.append(adapted)

    page_title = "Content Added Recently by %s" % context.title
    api = TemplateAPI(context, request, page_title)
    return dict(api=api,
             batch_info=batch,
             recent_items=recent_items)

def may_leave(userid, community):
    # May not leave community if a moderator
    return userid not in community.moderator_names

    # Alternatively, may not leave community if *sole* moderator
    # may_leave = len(community.moderator_names) > 1 or \
    #           userid not in community.moderator_names

def manage_communities_view(context, request):
    page_title = 'Manage Communities'
    api = TemplateAPI(context, request, page_title)

    users = find_users(context)
    communities_folder = find_communities(context)
    userid = context.__name__

    # Handle cancel
    if request.params.get("form.cancel", False):
        return HTTPFound(location=resource_url(context, request))

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

        path = resource_url(context, request)
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
                    { "value": IProfile.ALERT_DAILY_DIGEST,
                      "label": "Daily Digest",
                      "selected": alerts_pref == IProfile.ALERT_DAILY_DIGEST,
                    },
                    { "value": IProfile.ALERT_NEVER,
                      "label": "Never",
                      "selected": alerts_pref == IProfile.ALERT_NEVER,
                    },
                    { "value": IProfile.ALERT_WEEKLY_DIGEST,
                      "label": "Weekly Digest",
                      "selected": alerts_pref == IProfile.ALERT_WEEKLY_DIGEST,
                    },
                    { "value": IProfile.ALERT_BIWEEKLY_DIGEST,
                      "label": "Every two weeks Digest",
                      "selected": alerts_pref == IProfile.ALERT_BIWEEKLY_DIGEST,
                    },
                ],
                'may_leave': may_leave(userid, community),
            }
            communities.append(display_community)

    if len(communities) > 1:
        communities.sort(key=lambda x: x["title"])

    return render_to_response(
        'karl.views:templates/manage_communities.pt',
        dict(api=api,
             communities=communities,
             post_url=request.url,
             formfields=api.formfields,
             attachments=context.alert_attachments),
        request=request,
    )

def show_profiles_view(context, request):
    """
    This view is basically deprecated.  If there is a people directory present,
    we'll redirect there.
    """
    people = find_peopledirectory(context)
    if people:
        return HTTPFound(request.resource_url(people))

    # No people directory, show basic listing of profiles
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

    return render_to_response(
        'templates/profiles.pt',
        dict(api=api,
             profiles=profiles,
             letters=letter_info),
        request=request,
        )


class ChangePasswordFormController(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def form_fields(self):
        users = find_users(self.context)
        userid = self.context.__name__
        user = users.get_by_id(userid)
        old_password_field = schemaish.String(
            title="Old Password",
            validator=validator.All(
                validator.Required(),
                karlvalidators.CorrectUserPassword(user),
                )
            )
        new_password_field = schemaish.String(
            title="New Password",
            validator=validator.All(
                            karlvalidators.PasswordLength(min_pw_length()),
                            validator.Required())
            )
        fields = [('old_password', old_password_field),
                  ('password', new_password_field),
                  ]
        return fields

    def form_widgets(self, fields):
        widgets = {'old_password': formish.Password(),
                   'password': karlwidgets.KarlCheckedPassword()}
        return widgets

    def __call__(self):
        api = TemplateAPI(self.context, self.request, 'Change Password')
        layout_provider = get_layout_provider(self.context, self.request)
        layout = layout_provider('generic')
        snippets = get_renderer('forms/templates/snippets.pt').implementation()
        snippets.doctime = xhtml
        blurb_macro = snippets.macros['change_password_blurb']
        return {'api': api, 'layout': layout,
                'actions': [],
                'blurb_macro': blurb_macro}

    def handle_cancel(self):
        return HTTPFound(location=resource_url(self.context, self.request))

    def handle_submit(self, converted):
        context = self.context
        users = find_users(context)
        userid = context.__name__
        new_password = converted['password']
        sha_password = get_sha_password(new_password)
        if context.last_passwords is None:
            context.last_passwords = PersistentList()
        if sha_password in context.last_passwords:
            msg = "Please use a password that was not previously used"
            raise ValidationError(password=msg)
        users.change_password(userid, new_password)
        context.last_passwords.append(sha_password)
        if len(context.last_passwords) > 10:
            context.last_passwords = context.last_passwords[1:]
        self.request.session['password_expired'] = False
        context.password_expiration_date = (datetime.utcnow()
                                            + timedelta(days=180))

        path = resource_url(context, self.request)
        msg = '?status_message=Password%20changed'
        return HTTPFound(location=path+msg)


def deactivate_profile_view(context, request):
    page_title = 'Deactivate user account for %s %s' % (context.firstname,
                                                        context.lastname)
    api = TemplateAPI(context, request, page_title)

    name = context.__name__
    myself = authenticated_userid(request) == context.__name__

    if not api.user_is_admin and not myself:
        raise Forbidden("Only owner or admin can deactivate profile")

    confirm = request.params.get('confirm')
    if confirm:
        try:
            find_users(context).remove(name)
        except KeyError:
            pass
        workflow = get_workflow(IProfile, 'security', context)
        workflow.transition_to_state(context, request, 'inactive')
        if myself:
            return logout_view(context, request, reason='User removed')
        query = {'status_message': 'Deactivated user account: %s' % name}
        parent = context.__parent__
        location = resource_url(parent, request, query=query)

        return HTTPFound(location=location)

    # Show confirmation page.
    return dict(api=api, myself=myself)

def reactivate_profile_view(context, request,
                            reset_password=request_password_reset):
    name = context.__name__
    confirm = request.params.get('confirm')
    if confirm:
        users = find_users(context)
        temp_passwd = str(uuid.uuid4())
        users.add(name, name, temp_passwd, [])
        workflow = get_workflow(IProfile, 'security', context)
        workflow.transition_to_state(context, request, 'active')
        reset_password(users.get_by_id(name), context, request)
        query = {'status_message': 'Reactivated user account: %s' % name}
        location = resource_url(context, request, query=query)

        return HTTPFound(location=location)

    page_title = 'Reactivate user account for %s %s' % (context.firstname,
                                                        context.lastname)
    api = TemplateAPI(context, request, page_title)

    # Show confirmation page.
    return dict(api=api)
