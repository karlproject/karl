from __future__ import with_statement

import codecs
from cStringIO import StringIO
import csv
from _csv import Error
from repoze.postoffice.message import Message
import os
import re
import transaction
from paste.fileapp import FileApp
from webob import Response
from webob.exc import HTTPFound

from zope.component import getUtility

from repoze.bfg.chameleon_zpt import get_template
from repoze.bfg.exceptions import NotFound
from repoze.bfg.security import authenticated_userid
from repoze.bfg.traversal import find_model
from repoze.bfg.traversal import model_path
from repoze.bfg.url import model_url
from repoze.lemonade.content import create_content
from repoze.postoffice.queue import open_queue
from repoze.sendmail.interfaces import IMailDelivery
from repoze.workflow import get_workflow

from karl.content.interfaces import IBlogEntry
from karl.content.interfaces import ICalendarEvent
from karl.content.interfaces import IWikiPage
from karl.models.interfaces import ICatalogSearch
from karl.models.interfaces import ICommunity
from karl.models.interfaces import ICommunityContent
from karl.models.interfaces import IProfile
from karl.utilities.rename_user import rename_user

from karl.utils import find_community
from karl.utils import find_profiles
from karl.utils import find_site
from karl.utils import find_site
from karl.utils import find_users
from karl.utils import get_setting
from karl.views.api import TemplateAPI
from karl.views.utils import make_unique_name
from karl.views.batch import get_fileline_batch

class AdminTemplateAPI(TemplateAPI):

    def __init__(self, context, request, page_title=None):
        super(AdminTemplateAPI, self).__init__(context, request, page_title)
        syslog_view = get_setting(context, 'syslog_view', None)
        self.syslog_view_enabled = syslog_view != None
        self.has_logs = not not get_setting(context, 'logs_view', None)
        self.error_monitoring = not not get_setting(
            context, 'error_monitor_subsystems', None
        )
        statistics_folder = get_setting(context, 'statistics_folder', None)
        if statistics_folder is not None:
            csv_files = [fn for fn in os.listdir(statistics_folder)
                         if fn.endswith('.csv')]
            self.statistics_view_enabled = not not csv_files
        else:
            self.statistics_view_enabled = False

        use_postoffice = not not get_setting(
            context, 'postoffice.zodb_uri', False)
        if use_postoffice:
            self.quarantine_url = ('%s/po_quarantine.html' %
                                   request.application_url)
        else:
            self.quarantine_url = ('%s/mailin/quarantine' %
                                   request.application_url)

        site = find_site(context)
        if 'offices' in site:
            self.offices_url = model_url(site['offices'], request)
        else:
            self.offices_url = None

def _menu_macro():
    return get_template('templates/admin/menu.pt').macros['menu']

def admin_view(context, request):
    return dict(
        api=AdminTemplateAPI(context, request, 'Admin UI'),
        menu=_menu_macro()
    )

def _content_selection_widget():
    return get_template('templates/admin/content_select.pt').macros['widget']

def _content_selection_grid():
    return get_template('templates/admin/content_select.pt').macros['grid']

def _format_date(d):
    return d.strftime("%m/%d/%Y %H:%M")

def _populate_content_selection_widget(context, request):
    """
    Returns a dict of parameters to be passed to the template that includes
    the content selection widget.
    """
    # Get communities list
    search = ICatalogSearch(context)
    count, docids, resolver = search(
        interfaces=[ICommunity],
        sort_index='title'
    )
    communities = []
    for docid in docids:
        community = resolver(docid)
        communities.append(dict(
            path=model_path(community),
            title=community.title,
        ))

    return dict(
        communities=communities,
        title_contains=request.params.get('title_contains', None),
        selected_community=request.params.get('community', None),
    )

def _grid_item(item, request):
    creator_name, creator_url = 'Unknown', None
    profiles = find_profiles(item)
    creator = getattr(item, 'creator', None)
    if creator is not None and creator in profiles:
        profile = profiles[creator]
        creator_name = profile.title
        creator_url = model_url(profile, request)

    return dict(
        path=model_path(item),
        url=model_url(item, request),
        title=item.title,
        modified=_format_date(item.modified),
        creator_name=creator_name,
        creator_url=creator_url,
    )

def _get_filtered_content(context, request, interfaces=None):
    if interfaces is None:
        interfaces = [ICommunityContent,]
    search = ICatalogSearch(context)
    search_terms = dict(
        interfaces={'query': interfaces, 'operator': 'or'},
    )

    community = request.params.get('community', '_any')
    if community != '_any':
        search_terms['path'] = community

    title_contains = request.params.get('title_contains', '')
    if title_contains:
        title_contains = title_contains.lower()
        search_terms['texts'] = title_contains

    if community == '_any' and not title_contains:
        # Avoid retrieving entire site
        return []

    items = []
    count, docids, resolver = search(**search_terms)
    for docid in docids:
        item = resolver(docid)
        if (title_contains and title_contains not in
            getattr(item, 'title', '').lower()):
            continue
        items.append(_grid_item(item, request))

        # Try not to run out of memory
        if hasattr(item, '_p_deactivate'):
            item._p_deactivate()

    items.sort(key=lambda x: x['path'])
    return items

def delete_content_view(context, request):
    api = AdminTemplateAPI(context, request, 'Admin UI: Delete Content')
    filtered_content = []

    if 'filter_content' in request.params:
        filtered_content = _get_filtered_content(context, request)
        if not filtered_content:
            api.status_message = 'No content matches your query.'

    if 'delete_content' in request.params:
        paths = request.params.getall('selected_content')
        if paths:
            for path in paths:
                try:
                    content = find_model(context, path)
                    del content.__parent__[content.__name__]
                except KeyError:
                    # Thrown by find_model if we've already deleted an
                    # ancestor of this node.  Can safely ignore becuase child
                    # node has been deleted along with ancestor.
                    pass

            if len(paths) == 1:
                status_message = 'Deleted one content item.'
            else:
                status_message = 'Deleted %d content items.' % len(paths)

            redirect_to = model_url(
                context, request, request.view_name,
                query=dict(status_message=status_message)
            )
            return HTTPFound(location=redirect_to)

    parms = dict(
        api=api,
        menu=_menu_macro(),
        content_select_widget=_content_selection_widget(),
        content_select_grid=_content_selection_grid(),
        filtered_content=filtered_content,
    )
    parms.update(_populate_content_selection_widget(context, request))
    return parms

class _DstNotFound(Exception):
    pass

def _find_dst_container(src_obj, dst_community):
    """
    Given a source object and a destination community, figures out the
    container insider the destination community where source object can be
    moved to.  For example, if source object is a blog entry in community
    `foo` (/communities/foo/blog/entry1) and we want to move it to the `bar`
    community, this will take the relative path of the source object from its
    community and attempt to find analogous containers inside of the
    destination community.  In this example, the relative container path is
    'blog', so we the destination container is /communities/bar/blog.'
    """
    src_container_path = model_path(src_obj.__parent__)
    src_community_path = model_path(find_community(src_obj))
    rel_container_path = src_container_path[len(src_community_path):]
    dst_container = dst_community
    for node_name in filter(None, rel_container_path.split('/')):
        dst_container = dst_container.get(node_name, None)
        if dst_container is None:
            raise _DstNotFound(
                'Path does not exist in destination community: %s' %
                model_path(dst_community) + rel_container_path
            )
    return dst_container

def move_content_view(context, request):
    """
    Move content from one community to another.  Only blog entries supported
    for now.  May or may not eventually expand to other content types.
    """
    api = AdminTemplateAPI(context, request, 'Admin UI: Move Content')
    filtered_content = []

    if 'filter_content' in request.params:
        # We're limiting ourselves to content that always lives in the same
        # place in each community, ie /blog, /calendar, /wiki, etc, so that
        # we can be pretty sure we can figure out where inside the destination
        # community we should move it to.
        filtered_content = _get_filtered_content(
            context, request, [IBlogEntry, IWikiPage, ICalendarEvent])
        if not filtered_content:
            api.error_message = 'No content matches your query.'

    if 'move_content' in request.params:
        to_community = request.params.get('to_community', '')
        if not to_community:
            api.error_message = 'Please specify destination community.'
        else:
            try:
                paths = request.params.getall('selected_content')
                dst_community = find_model(context, to_community)
                for path in paths:
                    obj = find_model(context, path)
                    dst_container = _find_dst_container(obj, dst_community)
                    name = make_unique_name(dst_container, obj.__name__)
                    del obj.__parent__[obj.__name__]
                    dst_container[name] = obj

                if len(paths) == 1:
                    status_message = 'Moved one content item.'
                else:
                    status_message = 'Moved %d content items.' % len(paths)

                redirect_to = model_url(
                    context, request, request.view_name,
                    query=dict(status_message=status_message)
                )
                return HTTPFound(location=redirect_to)
            except _DstNotFound, error:
                api.error_message = str(error)

    parms = dict(
        api=api,
        menu=_menu_macro(),
        content_select_widget=_content_selection_widget(),
        content_select_grid=_content_selection_grid(),
        filtered_content=filtered_content,
    )
    parms.update(_populate_content_selection_widget(context, request))
    return parms

def site_announcement_view(context, request):
    """
    Edit the text of the site announcement, which will be displayed on
    every page for every user of the site.
    """
    if 'submit-site-announcement' in request.params:
        site = find_site(context)
        annc = request.params.get('site-announcement-input', '').strip()
        if annc:
            # we only take the content of the first <p> tag, with
            # the <p> tags stripped
            paramatcher = re.compile('<[pP]\\b[^>]*>(.*?)</[pP]>')
            match = paramatcher.search(annc)
            if match is not None:
                annc = match.groups()[0]
            site.site_announcement = annc
    if 'remove-site-announcement' in request.params:
        site = find_site(context)
        site.site_announcement = u''
    api = AdminTemplateAPI(context, request, 'Admin UI: Move Content')
    return dict(
        api=api,
        menu=_menu_macro()
        )


class EmailUsersView(object):
    # The groups are a pretty obvious customization point, so we make this view
    # a class so that customization packages can subclass this and override
    # the groups.
    to_groups = [
        ('group.KarlStaff', 'Staff'),
        ('', 'Everyone'),
    ]

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        context, request = self.context, self.request
        api = AdminTemplateAPI(context, request, 'Admin UI: Send Email')
        admin_email = get_setting(context, 'admin_email')
        system_name = get_setting(context, 'system_name')
        profiles = find_profiles(context)
        admin = profiles[authenticated_userid(request)]
        from_emails = [
            ('self', '%s <%s>' % (admin.title, admin.email)),
            ('admin', '%s Administrator <%s>' % (system_name, admin_email)),
        ]

        if 'send_email' in request.params:
            mailer = getUtility(IMailDelivery)
            group = request.params['to_group']
            users = find_users(context)
            search = ICatalogSearch(context)
            count, docids, resolver = search(interfaces=[IProfile])
            n = 0
            for docid in docids:
                profile = resolver(docid)
                userid = profile.__name__
                if group and not users.member_of_group(userid, group):
                    continue

                message = Message()
                if request.params['from_email'] == 'self':
                    message['From'] = from_emails[0][1]
                    message_from = admin.email
                else:
                    message['From'] = from_emails[1][1]
                    message_from = admin_email
                message['To'] = '%s <%s>' % (profile.title, profile.email)
                message['Subject'] = request.params['subject']
                body = u'<html><body>%s</body></html>' % (
                    request.params['text']
                )
                message.set_payload(body.encode('UTF-8'), 'UTF-8')
                message.set_type('text/html')

                mailer.send([profile.email], message)
                n += 1

            status_message = "Sent message to %d users." % n
            redirect_to = model_url(context, request, 'admin.html',
                                    query=dict(status_message=status_message))
            return HTTPFound(location=redirect_to)

        return dict(
            api=api,
            menu=_menu_macro(),
            to_groups = self.to_groups,
            from_emails=from_emails,
        )

def syslog_view(context, request):
    syslog_path = get_setting(context, 'syslog_view')
    instances = get_setting(context, 'syslog_view_instances', ['karl'])
    filter_instance = request.params.get('instance', '_any')
    if filter_instance == '_any':
        filter_instances = instances
    else:
        filter_instances = [filter_instance]

    def line_filter(line):
        try:
            month, day, time, host, instance, message = line.split(None, 5)
        except ValueError:
            # Ignore lines that don't fit the format
            return None

        if instance not in filter_instances:
            return None

        return line

    if syslog_path:
        syslog = codecs.open(syslog_path, encoding='utf-8',
                             errors='replace')
    else:
        syslog = StringIO()

    batch_info = get_fileline_batch(syslog, context, request,
                                    line_filter=line_filter, backwards=True)

    return dict(
        api=AdminTemplateAPI(context, request),
        menu=_menu_macro(),
        instances=instances,
        instance=filter_instance,
        batch_info=batch_info,
    )

def logs_view(context, request):
    log_paths = get_setting(context, 'logs_view')
    if len(log_paths) == 1:
        # Only one log file, just view that
        log = log_paths[0]

    else:
        # Make user pick a log file
        log = request.params.get('log', None)

        # Don't let users view arbitrary files on the filesystem
        if log not in log_paths:
            log = None

    if log is not None and os.path.exists(log):
        lines = codecs.open(log, encoding='utf-8',
                            errors='replace').readlines()
    else:
        lines = []

    return dict(
        api=AdminTemplateAPI(context, request),
        menu=_menu_macro(),
        logs=log_paths,
        log=log,
        lines=lines,
    )

def statistics_view(context, request):
    statistics_folder = get_setting(context, 'statistics_folder')
    csv_files = [fn for fn in os.listdir(statistics_folder)
                 if fn.endswith('.csv')]
    return dict(
        api=AdminTemplateAPI(context, request),
        menu=_menu_macro(),
        csv_files=csv_files
    )

def statistics_csv_view(request):
    statistics_folder = get_setting(request.context, 'statistics_folder')
    csv_file = request.matchdict.get('csv_file')
    if not csv_file.endswith('.csv'):
        raise NotFound()

    path = os.path.join(statistics_folder, csv_file)
    if not os.path.exists(path):
        raise NotFound()

    return request.get_response(FileApp(path).get)

class UploadUsersView(object):
    rename_user = rename_user

    required_fields = [
        'username',
        'email',
        'firstname',
        'lastname',
    ]

    allowed_fields = required_fields + [
        'phone',
        'extension',
        'department',
        'position',
        'organization',
        'location',
        'country',
        'website',
        'languages',
        'office',
        'room_no',
        'biography',
        'home_path',
        'login',
        'groups',
        'password',
        'sha_password',
    ]

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        context = self.context
        request = self.request

        errors = []
        messages = []

        # Handle CSV upload
        field = request.params.get('csv', None)
        if hasattr(field, 'file'):
            reactivate = request.params.get('reactivate') == 'true'
            reader = csv.DictReader(field.file)
            try:
                rows = list(reader)
            except Error, e:
                errors.append("Malformed CSV: %s" % e[0])

            # Make sure we have required fields
            if not errors:
                fieldnames = rows[0].keys()
                if None in fieldnames:
                    errors.append(
                        "Malformed CSV: line 2 does not match header."
                    )
                else:
                    for required_field in self.required_fields:
                        if required_field not in fieldnames:
                            errors.append("Missing required field: %s" %
                                          required_field)
                    if (not ('password' in fieldnames or
                        'sha_password' in fieldnames)):
                        errors.append('Must supply either password or '
                                      'sha_password field.')

                    # Restrict to allowed fields
                    allowed_fields = self.allowed_fields
                    for fieldname in fieldnames:
                        if fieldname not in allowed_fields:
                            errors.append("Unrecognized field: %s" % fieldname)

            # Add users
            if not errors:
                search = ICatalogSearch(context)
                profiles = find_profiles(context)
                users = find_users(context)

                n_added = 0
                for i, row in enumerate(rows):
                    row_has_errors = False
                    if None in row or None in row.values():
                        errors.append(
                            "Malformed CSV: line %d does not match header." %
                            (i+2))
                        break
                    added_users, row_messages, row_errors = (
                        self._add_user_csv_row(search, profiles, users, row,
                                          reactivate, i)
                    )
                    n_added += added_users
                    messages += row_messages
                    errors += row_errors

                if not errors:
                    messages.append("Created %d users." % n_added)

        if errors:
            transaction.doom()

        api = AdminTemplateAPI(context, request)
        api.error_message = '\n'.join(errors)
        api.status_message = '\n'.join(messages)

        return dict(
            api=api,
            menu=_menu_macro(),
            required_fields=self.required_fields,
            allowed_fields=self.allowed_fields,
        )

    def _add_user_csv_row(self, search, profiles, users, row, reactivate, i):
        errors = []
        messages = []

        username = row.pop('username')
        login = row.pop('login', username)
        if not username:
            errors.append(
                "Malformed CSV: line %d has an empty username." %
                (i+2))

        email = row['email']
        if not email:
            errors.append(
                'Malformed CSV: line %d has an empty email address.' % (i+2)
            )

        if errors:
            return 0, messages, errors

        website = row.pop('website', None)
        if website is not None:
            row['websites'] = website.strip().split()

        profile = profiles.get(username)
        skip = False
        if (users.get_by_id(username) is not None or
            (profile is not None and profile.security_state != 'inactive')):
            messages.append(
                "Skipping user: %s: User already exists." %
                username
            )
            skip = True
        elif users.get_by_login(login):
            messages.append(
                "Skipping user: %s: User already exists with "
                "login: %s" % (username, login)
            )
            skip = True

        if skip:
            return 0, messages, errors

        merge_profile = None
        count, docids, resolver = search(email=email)
        if count > 1:
            errors.append(
                'Multiple users already exist with email '
                'address: %s' % email
            )
        elif count == 1:
            merge_profile = resolver(docids[0])
            if merge_profile.security_state != 'inactive':
                errors.append(
                    'An active user already exists with email '
                    'address: %s.' % email
                )
            elif not reactivate:
                errors.append(
                    'A previously deactivated user exists with '
                    'email address: %s.  Consider checking the '
                    '"Reactivate user" checkbox to reactivate '
                    'the user.' % email
                )

            if merge_profile.__name__ == username:
                merge_profile = None

        if profile is None:
            profile = profiles.get(username)
            if profile is not None and not reactivate:
                errors.append(
                    'A previously deactivated user exists with username: %s.  '
                    'Consider checking the "Reactivate user" checkbox to '
                    'reactivate the user.' % username
                )

        if errors:
            return 0, messages, errors

        groups = row.pop('groups', '')
        groups = set(groups.split())
        if 'sha_password' in row:
            users.add(username, login, row.pop('sha_password'),
                      groups, encrypted=True)
        else:
            users.add(username, login, row.pop('password'),
                      groups)
        decoded = {}
        for k, v in row.items():
            if isinstance(v, str):
                try:
                    v = v.decode('utf8')
                except UnicodeDecodeError:
                    v = v.decode('latin1')
            decoded[k] = v
        if profile is None:
            profile = create_content(IProfile, **decoded)
            profiles[username] = profile
            workflow = get_workflow(IProfile, 'security', profile)
            if workflow is not None:
                workflow.initialize(profile)
        else:
            messages.append('Reactivated %s.' % username)
            for k, v in decoded.items():
                setattr(profile, k, v)
            workflow = get_workflow(IProfile, 'security', profile)
            workflow.transition_to_state(profile, None, 'active')

        if merge_profile is not None:
            merge_messages = StringIO()
            self.rename_user(profile, merge_profile.__name__, username,
                             merge=True, out=merge_messages)
            messages += merge_messages.getvalue().split('\n')

        return 1, messages, errors

def _decode(s):
    """
    Convert to unicode, by hook or crook.
    """
    try:
        return s.decode('utf-8')
    except UnicodeDecodeError:
        # Will probably result in some junk characters but it's better than
        # nothing.
        return s.decode('latin-1')

def _get_error_monitor_state(error_monitor_dir, subsystem):
    status_file = os.path.join(error_monitor_dir, subsystem)
    if os.path.exists(status_file) and os.path.getsize(status_file) > 0:
        errors = open(status_file, 'rb').read()
        return filter(None, [_decode(entry.strip()) for entry in
                             errors.split('ENTRY\n')])
    return []

def error_monitor_view(context, request):
    error_monitor_dir = get_setting(context, 'error_monitor_dir', '')
    subsystems = get_setting(context, 'error_monitor_subsystems')
    states = {}
    urls = {}
    for subsystem in subsystems:
        urls[subsystem] = model_url(context, request,
                                    'error_monitor_subsystem.html',
                                    query={'subsystem': subsystem})
        states[subsystem] = _get_error_monitor_state(
            error_monitor_dir, subsystem
        )

    # Tack on mailin quarantine status while we're at it
    use_postoffice = not not get_setting(
        context, 'postoffice.zodb_uri', False)
    if  use_postoffice:
        name = 'postoffice quarantine'
        urls[name] = '%s/po_quarantine.html' % request.application_url
        queue, closer = _get_postoffice_queue(request.context)
        if queue.count_quarantined_messages() > 0:
            states[name] = ['Messages in quarantine.']
        else:
            states[name] = []
        subsystems = list(subsystems)
        subsystems.append(name)

    return dict(
        api=AdminTemplateAPI(context, request),
        menu=_menu_macro(),
        subsystems=subsystems,
        urls=urls,
        states=states,
    )

def error_monitor_subsystem_view(context, request):
    error_monitor_dir = get_setting(context, 'error_monitor_dir', '')
    subsystems = get_setting(context, 'error_monitor_subsystems')
    subsystem = request.params.get('subsystem', None)
    if subsystem is None or subsystem not in subsystems:
        raise NotFound()

    entries = _get_error_monitor_state(error_monitor_dir, subsystem)
    back_url = model_url(context, request, 'error_monitor.html')

    return dict(
        api=AdminTemplateAPI(context, request),
        menu=_menu_macro(),
        subsystem=subsystem,
        entries=entries,
        back_url=back_url,
    )

def error_monitor_status_view(context, request):
    """
    Simple text only view that shows only error state, for use with external
    monitoring.
    """
    error_monitor_dir = get_setting(context, 'error_monitor_dir')
    subsystems = get_setting(context, 'error_monitor_subsystems')
    subsystems = subsystems + ['postoffice quarantine']

    req_subsystems = request.params.getall('subsystem')
    if req_subsystems:
        subsystems = filter(lambda x: x in subsystems, req_subsystems)

    buf = StringIO()
    for subsystem in subsystems:
        # Special case postoffice quarantine
        if subsystem == 'postoffice quarantine':
            use_postoffice = not not get_setting(
                context, 'postoffice.zodb_uri', False)
            if  use_postoffice:
                queue, closer = _get_postoffice_queue(request.context)
                if queue.count_quarantined_messages() == 0:
                    print >>buf, 'postoffice quarantine: OK'
                else:
                    print >>buf, 'postoffice quarantine: ERROR'

        # Normal case
        elif _get_error_monitor_state(error_monitor_dir, subsystem):
            print >>buf, '%s: ERROR' % subsystem
        else:
            print >>buf, '%s: OK' % subsystem

    return Response(buf.getvalue(), content_type='text/plain')

_mailin_monitor_app = None
def mailin_monitor_view(context, request):
    """
    Dispatches to a subapp from repoze.mailin.monitor.  I know this looks kind
    of horrible, but this is the best way I know how to mount another object
    graph onto the root object graph in BFG 1.2.  BFG 1.3 will theoretically
    allow SCRIPT_NAME/PATH_INFO rewriting for routes of the form
    '/some/path/*traverse', making it easier to do this with just a route,
    rather than actually constituting a whole new bfg app just to serve this
    subtree.
    """
    global _mailin_monitor_app
    if _mailin_monitor_app is None:
        # Keep imports local in hopes that this can be removed when BFG 1.3
        # comes out.
        from repoze.bfg.authorization import ACLAuthorizationPolicy
        from repoze.bfg.configuration import Configurator
        from karl.models.mailin_monitor import KarlMailInMonitor
        from karl.security.policy import get_groups
        from repoze.bfg.authentication import RepozeWho1AuthenticationPolicy

        authentication_policy = RepozeWho1AuthenticationPolicy(
            callback=get_groups
        )
        authorization_policy = ACLAuthorizationPolicy()
        config = Configurator(root_factory=KarlMailInMonitor(),
                              authentication_policy=authentication_policy,
                              authorization_policy=authorization_policy)
        config.begin()
        config.load_zcml('repoze.mailin.monitor:configure.zcml')
        config.end()
        _mailin_monitor_app = config.make_wsgi_app()

    # Dispatch to subapp
    import webob
    sub_environ = request.environ.copy()
    sub_environ['SCRIPT_NAME'] = '/%s/%s' % (model_path(context),
                                            request.view_name)
    sub_environ['PATH_INFO'] = '/' + '/'.join(request.subpath)
    sub_request = webob.Request(sub_environ)
    return sub_request.get_response(_mailin_monitor_app)

def _get_postoffice_queue(context):
    zodb_uri = get_setting(context, 'postoffice.zodb_uri')
    queue_name = get_setting(context, 'postoffice.queue')
    return open_queue(zodb_uri, queue_name)

def postoffice_quarantine_view(request):
    """
    See messages in postoffice quarantine.
    """
    context = request.context
    queue, closer = _get_postoffice_queue(context)

    if request.params:
        for key in request.params.keys():
            if key.startswith('delete_'):
                message_id = key.split('_')[1]
                if message_id == 'all':
                    messages = [message for message, error in
                                queue.get_quarantined_messages()]
                    for message in messages:
                        queue.remove_from_quarantine(message)
                else:
                    queue.remove_from_quarantine(
                        queue.get_quarantined_message(message_id)
                    )
            elif key.startswith('requeue_'):
                message_id = key.split('_')[1]
                if message_id == 'all':
                    messages = [message for message, error in
                                queue.get_quarantined_messages()]
                    for message in messages:
                        queue.remove_from_quarantine(message)
                        queue.add(message)
                else:
                    message = queue.get_quarantined_message(message_id)
                    queue.remove_from_quarantine(message)
                    queue.add(message)
        closer.conn.transaction_manager.commit()
        return HTTPFound(
            location=model_url(context, request, request.view_name)
        )

    messages = []
    for message, error in queue.get_quarantined_messages():
        po_id = message['X-Postoffice-Id']
        url = '%s/po_quarantine/%s' % (
            request.application_url, po_id
        )
        messages.append(
            dict(url=url, message_id=message['Message-Id'], po_id=po_id,
                 error=error)
        )

    return dict(
        api=AdminTemplateAPI(context, request),
        menu=_menu_macro(),
        messages=messages
    )

def postoffice_quarantine_status_view(request):
    """
    Report status of quarantine.  If no messages are in quarantine, status is
    'OK', otherwise status is 'ERROR'.
    """
    queue, closer = _get_postoffice_queue(request.context)
    if queue.count_quarantined_messages() == 0:
        return Response('OK')
    return Response('ERROR')

def postoffice_quarantined_message_view(request):
    """
    View a message in the postoffice quarantine.
    """
    queue, closer = _get_postoffice_queue(request.context)
    id = request.matchdict.get('id')
    try:
        msg = queue.get_quarantined_message(id)
    except KeyError:
        raise NotFound
    return Response(body=msg.as_string(), content_type='text/plain')

def rename_or_merge_user_view(request, rename_user=rename_user):
    """
    Rename or merge users.
    """
    context = request.context
    api=AdminTemplateAPI(context, request)
    old_username = request.params.get('old_username')
    new_username = request.params.get('new_username')
    if old_username and new_username:
        merge = bool(request.params.get('merge'))
        rename_messages = StringIO()
        try:
            rename_user(context, old_username, new_username, merge=merge,
                        out=rename_messages)
            api.status_message = rename_messages.getvalue()
        except ValueError, e:
            api.error_message = str(e)

    return dict(
        api=api,
        menu=_menu_macro()
    )
