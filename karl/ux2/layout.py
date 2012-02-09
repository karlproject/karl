import os
import sys
import time

from subprocess import PIPE
from subprocess import Popen

from bottlecap.layouts.popper.layout import PopperLayout

from pyramid.decorator import reify
from pyramid.renderers import get_renderer
from pyramid.security import effective_principals
from pyramid.security import has_permission
from pyramid.traversal import find_resource
from pyramid.url import resource_url

from karl.security.policy import VIEW
from karl.utils import find_intranet
from karl.utils import find_site


class Layout(PopperLayout):
    page_title = 'Page Title'

    def __init__(self, context, request):
        super(Layout, self).__init__(context, request)
        self.settings = settings = request.registry.settings

        self.app_url = app_url = request.application_url
        self.here_url = resource_url(context, request)
        self.current_intranet = find_intranet(context)
        self.people_url = app_url + '/' + settings.get('people_path', 'people')
        self.site = find_site(context)
        self.karl_static = '%s/static/%s' % (app_url, _get_static_rev())
        self.project_name = settings.get('system_name', 'KARL')
        self.extra_css = ['%s/ux2/main.css' % self.karl_static]

    @reify
    def should_show_calendar_tab(self):
        path = self.settings.get('global_calendar_path', '/offices/calendar')
        try:
            calendar = find_resource(self.context, path)
        except KeyError:
            return False

        return has_permission(VIEW, calendar, self.request)

    @reify
    def user_is_staff(self):
        return 'group.KarlStaff' in effective_principals(self.request)

    @reify
    def user_is_admin(self):
        return 'group.KarlAdmin' in effective_principals(self.request)

    @reify
    def macros(self):
        return get_renderer('templates/macros.pt').implementation().macros


_static_rev = None


def _get_static_rev():
    global _static_rev
    if _static_rev is not None:
        return _static_rev

    # If Karl is installed via an egg, we can try to get the Karl version
    # number from the egg and use that.
    _static_rev = _get_egg_rev()

    if _static_rev is not None:
        return _static_rev

    # Development builds will use a checked out SVN copy.  See if we can
    # get the SVN revision number.
    _static_rev = _get_svn_rev()

    if _static_rev is not None:
        return _static_rev

    # Fallback to just using a timestamp.  This is guaranteed not to fail
    # but will create different revisions for each process, resulting in
    # some extra static resource downloads
    _static_rev = 'r%d' % int(time.time())

    return _static_rev

def _get_svn_rev():
    module = sys.modules[__name__]
    path = os.path.dirname(os.path.abspath(module.__file__))
    try:
        proc = Popen(['svn', 'info', path], stdout=PIPE, stderr=PIPE,
                     close_fds=True)
        output = proc.stdout.readlines()
        proc.stdout.close()
        proc.stderr.close() # Ignore
        for line in output:
            if line.startswith('Revision:'):
                rev = int(line.split(':')[1])
                return 'r%d' % rev
    except OSError:
        pass

def _get_egg_rev():
    # Find folder that this module is contained in
    module = sys.modules[__name__]
    path = os.path.dirname(os.path.abspath(module.__file__))

    # Walk up the tree until we find the parent folder of an EGG-INFO folder.
    while path != '/':
        egg_info = os.path.join(path, 'EGG-INFO')
        if os.path.exists(egg_info):
            rev = os.path.split(path)[1]
            return 'r%d' % hash(rev)
        path = os.path.dirname(path)
