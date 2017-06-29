from webob.exc import HTTPFound

import formish
import schemaish

from pyramid.exceptions import NotFound
from pyramid_formish import ValidationError
from pyramid.security import authenticated_userid
from pyramid.url import resource_url

from karl.utils import find_users
from karl.utils import get_setting
from karl.utils import find_peopledirectory
from karl.views import peopledirectory
from karl.views.api import TemplateAPI
from karl.views.forms import validators as karlvalidators
from karl.views.forms import widgets as karlwidgets
from karl.views.forms.widgets import VerticalRadioChoice
from karl.views.people import AdminEditProfileFormController as AdminFCBase
from karl.views.people import EditProfileFormController
from karl.views.people import groups_field
from karl.views.people import login_field
from karl.views.people import show_profile_view
from karl.views.peopledirectory import get_actions
from karl.views.peopledirectory import get_admin_actions

from osi.utilities.former_staff import make_non_staff

min_pw_length = get_setting(None, 'min_pw_length', 8)


class AdminEditProfileFormController(AdminFCBase):
    def __init__(self, context, request):
        super(AdminEditProfileFormController, self).__init__(context,
                                                             request)
        users = self.users
        self.is_staff = users.member_of_group(self.userid,
                                              'group.KarlStaff')
        self.is_own_profile = context.__name__ == authenticated_userid(
            request)

    def __call__(self):
        kw = super(AdminEditProfileFormController, self).__call__()
        kw['is_own_profile'] = self.is_own_profile
        kw['is_staff'] = self.is_staff
        return kw

    # Same as core but omits staff password fields, as those are handled in GSA
    # for OSI.  Also conditionally adds field for action to take when user
    # becomes former staff.
    def form_fields(self):
        context = self.context
        home_path_field = schemaish.String(
            validator=karlvalidators.PathExists(context),
            description=('The first page to show after logging in. '
                         'Leave blank to show a community or the '
                         'community list.'))
        fields = []
        if self.user is not None:
            fields.append(('login', login_field))
            fields.append(('groups', groups_field))
        fields.append(('home_path', home_path_field))
        if self.is_staff:
            former_staff_action_field = schemaish.String(
                description='What action to take if user is no longer OSI '
                            'Staff.'
            )
            fields.insert(2, ('former_staff_action',
                              former_staff_action_field))
        elif self.user is not None:
            password_field = schemaish.String(
                validator=karlvalidators.PasswordLength(min_pw_length),
                title='Reset Password',
                description=('Enter a new password for the user here, '
                             'or leave blank to leave the password '
                             'unchanged.'))
            fields.insert(1, ('password', password_field))

        fields += super(AdminFCBase, self).form_fields()
        fields.append(('board', schemaish.String()))
        return fields

    def form_defaults(self):
        defaults = super(AdminEditProfileFormController, self).form_defaults()
        defaults['board'] = getattr(self.context, 'board', '')
        return defaults

    def form_widgets(self, fields):
        widgets = super(AdminFCBase, self).form_widgets(fields)
        if self.user is not None:
            groups_widget = formish.CheckboxMultiChoice(
                self.group_options)
            widgets.update({'login': formish.Input(empty=''),
                            'groups': groups_widget,
            })
        widgets['home_path'] = formish.Input(empty='')
        if self.is_staff:
            widgets['former_staff_action'] = VerticalRadioChoice(
                options=(
                    (None, 'No action'),
                    ('remove_and_notify',
                     'Remove user from all communities '
                     'and notify moderators'),
                    ('remove_only',
                     'Remove user from all communities without '
                     'notifying moderators'),
                ),
                none_option=None,
            )
        elif self.user is not None:
            widgets['password'] = karlwidgets.KarlCheckedPassword()

        return widgets

    def handle_submit(self, converted):
        to_former_staff = (self.is_staff and 'group.KarlStaff'
        not in converted['groups'])
        action = converted.get('former_staff_action', None)
        if not to_former_staff and action:
            raise ValidationError(
                former_staff_action='This option only available when removing '
                                    'user from KarlStaff group.'
            )

        if action:
            notify_moderators = action == 'remove_and_notify'
            make_non_staff(self.context, notify_moderators)

        board = converted.get('board')
        if board and board.strip():
            self.context.board = board
        else:
            self.context.board = None

        return super(AdminEditProfileFormController, self).handle_submit(
            converted)


class OsiEditProfileFormController(EditProfileFormController):
    # Same as core but adds a few extra values to dict used to render
    # form.
    def __call__(self):
        context = self.context
        kw = super(OsiEditProfileFormController, self).__call__()
        if isinstance(kw, dict):
            kw['is_own_profile'] = True
            users = find_users(context)
            userid = context.__name__
            kw['is_staff'] = users.member_of_group(userid, 'group.KarlStaff')
            kw['is_active'] = context.security_state == 'active'
        return kw

    # Same as core but omits staff password fields, as those are handled in GSA
    # for OSI.  Also conditionally adds field for action to take when user
    # becomes former staff.
    def form_fields(self):
        fields = super(OsiEditProfileFormController, self).form_fields()
        fields.insert(10, ('board', schemaish.String()))
        return fields

    def form_defaults(self):
        defaults = super(OsiEditProfileFormController, self).form_defaults()
        defaults['board'] = getattr(self.context, 'board', '')
        return defaults

    def handle_submit(self, converted):
        board = converted.get('board')
        if board and board.strip():
            self.context.board = board
        else:
            self.context.board = None

        return super(OsiEditProfileFormController, self).handle_submit(
            converted)

def osi_show_profile_view(context, request):
    info = show_profile_view(context, request)
    info['profile']['board'] = getattr(context, 'board', '')
    return info


def peopledirectory_view(context, request):
    """
    Overrides the core people directory view to intercept requests generated
    by OSI's old opensearch view, used by karl.peopledir rather than our newer
    core peopledir. This is to prevent all open searches already deployed in
    the wild from breaking when we migrate to core peopledir. In the event
    that the request is not an opensearch search request, we just call the
    core view.
    """
    if 'text' in request.params:
        # This is an opensearch request, redirect to real search form
        url = resource_url(context, request, 'all-karl', 'all-karl',
                           query=[('body', request.params['text'])])
        return HTTPFound(location=url)

    # Just do the default view
    return peopledirectory.peopledirectory_view(context, request)


def layouts_redirect_view(people, request):
    """
    Redirects requests for tabs in old people directory to tabs in the new
    people directory.  Tabs in old people directory were referred to as
    "layouts".
    """
    tab = request.subpath[0]
    if tab not in people:
        raise NotFound()
    section = people[tab]
    return HTTPFound(location=resource_url(section, request))


def searches_redirect_view(people, request):
    """
    Redirects requests for searches in old peopledirectory to reports in new
    people directory.  Old people directory urls do not contain any information
    about which section a search was in, so we have to traverse through our
    sections and find the report.
    """
    name = request.subpath[0]
    for section in people.values():
        if name in section:
            report = section[name]
            return HTTPFound(location=resource_url(report, request))

    raise NotFound()


def pdc_admin_contents(context, request):
    peopledir = find_peopledirectory(context)
    api = TemplateAPI(context, request, 'Contents')
    if 'form.delete' in request.POST:
        if 'selected' not in request.POST:
            api.status_message = 'Please select a value'
        else:
            for name in request.POST.getall('selected'):
                del context[name]
            return HTTPFound(location=resource_url(context, request,
                                                   'admin.html')
            )
    actions = get_admin_actions(context, request)
    del actions[0]  # Get rid of "Edit" action--doesn't make sense here.
    actions += get_actions(context, request)
    return dict(api=api,
                peopledir=peopledir,
                actions=actions,
                has_categories=peopledir is context,
    )
