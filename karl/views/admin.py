from __future__ import with_statement

import codecs
from cStringIO import StringIO
import csv
from _csv import Error
import datetime
import os
import re
import time
import transaction
import uuid

from operator import itemgetter

from repoze.postoffice.message import Message
from paste.fileapp import FileApp
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPBadRequest

from zope.component import getUtility

from pyramid.renderers import get_renderer
from pyramid.exceptions import NotFound
from pyramid.security import authenticated_userid
from pyramid.security import has_permission
from pyramid.traversal import find_resource
from pyramid.traversal import resource_path
from pyramid.url import resource_url
from repoze.lemonade.content import create_content
from repoze.postoffice.queue import open_queue
from repoze.sendmail.interfaces import IMailDelivery
from repoze.workflow import get_workflow

from karl.box.client import find_box
from karl.box.client import BoxClient
from karl.content.interfaces import IBlogEntry
from karl.content.interfaces import ICalendarEvent
from karl.content.interfaces import IWikiPage
from karl.models.interfaces import ICatalogSearch
from karl.models.interfaces import ICommunity
from karl.models.interfaces import ICommunityContent
from karl.models.interfaces import IInvitation
from karl.models.interfaces import IProfile
from karl.models.peopledirectory import is_staff
from karl.security.policy import ADMINISTER
from karl.utilities.converters.interfaces import IConverter
from karl.utilities.rename_user import rename_user

from karl.utils import asbool
from karl.utils import coarse_datetime_repr
from karl.utils import find_communities
from karl.utils import find_community
from karl.utils import find_profiles
from karl.utils import find_site
from karl.utils import find_users
from karl.utils import get_setting
from karl.views.api import TemplateAPI
from karl.views.utils import make_unique_name
from karl.views.batch import get_fileline_batch

class AdminTemplateAPI(TemplateAPI):

    def __init__(self, context, request, page_title=None):
        super(AdminTemplateAPI, self).__init__(context, request, page_title)
        settings = request.registry.settings
        syslog_view = get_setting(context, 'syslog_view', None)
        self.syslog_view_enabled = syslog_view != None
        self.has_logs = not not get_setting(context, 'logs_view', None)
        self.redislog = asbool(settings.get('redislog', 'False'))
        statistics_folder = get_setting(context, 'statistics_folder', None)
        if statistics_folder is not None and os.path.exists(statistics_folder):
            csv_files = [fn for fn in os.listdir(statistics_folder)
                         if fn.endswith('.csv')]
            self.statistics_view_enabled = not not csv_files
        else:
            self.statistics_view_enabled = False

        self.quarantine_url = ('%s/po_quarantine.html' %
                               request.application_url)

        site = find_site(context)
        if 'offices' in site:
            self.offices_url = resource_url(site['offices'], request)
        else:
            self.offices_url = None

        self.has_mailin = (
            get_setting(context, 'zodbconn.uri.postoffice') and
            get_setting(context, 'postoffice.queue'))

def _menu_macro():
    return get_renderer(
        'templates/admin/menu.pt').implementation().macros['menu']

def admin_view(context, request):
    return dict(
        api=AdminTemplateAPI(context, request, 'Admin UI'),
        menu=_menu_macro(),
    )

def _content_selection_widget():
    return get_renderer(
        'templates/admin/content_select.pt').implementation().macros['widget']

def _content_selection_grid():
    return get_renderer(
        'templates/admin/content_select.pt').implementation().macros['grid']

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
            path=resource_path(community),
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
        creator_url = resource_url(profile, request)

    return dict(
        path=resource_path(item),
        url=resource_url(item, request),
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
                    content = find_resource(context, path)
                    del content.__parent__[content.__name__]
                except KeyError:
                    # Thrown by find_resource if we've already deleted an
                    # ancestor of this node.  Can safely ignore becuase child
                    # node has been deleted along with ancestor.
                    pass

            if len(paths) == 1:
                status_message = 'Deleted one content item.'
            else:
                status_message = 'Deleted %d content items.' % len(paths)

            redirect_to = resource_url(
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
    src_container_path = resource_path(src_obj.__parent__)
    src_community_path = resource_path(find_community(src_obj))
    rel_container_path = src_container_path[len(src_community_path):]
    dst_container = dst_community
    for node_name in filter(None, rel_container_path.split('/')):
        dst_container = dst_container.get(node_name, None)
        if dst_container is None:
            raise _DstNotFound(
                'Path does not exist in destination community: %s' %
                resource_path(dst_community) + rel_container_path
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
                dst_community = find_resource(context, to_community)
                for path in paths:
                    obj = find_resource(context, path)
                    dst_container = _find_dst_container(obj, dst_community)
                    name = make_unique_name(dst_container, obj.__name__)
                    del obj.__parent__[obj.__name__]
                    dst_container[name] = obj

                if len(paths) == 1:
                    status_message = 'Moved one content item.'
                else:
                    status_message = 'Moved %d content items.' % len(paths)

                redirect_to = resource_url(
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

def archive_to_box_view(context, request):
    """
    Archive inactive communities to the Box storage service.
    """
    api = AdminTemplateAPI(context, request, 'Admin UI: Archive to Box')
    communities = None
    box = find_box(context)
    client = BoxClient(box, request.registry.settings)
    logged_in = False
    state = request.params.get('state', None)

    if state:
        if state == box.state:
	    client.authorize(request.params['code'])
	else:
            raise HTTPBadRequest("Box state does not match")
        state = box.state = None
	#return HTTPFound(request.path_url)

    if box.logged_in:
        logged_in = True
        # Find inactive communities
        search = ICatalogSearch(context)
        now = datetime.datetime.now()
        timeago = now - datetime.timedelta(days=425)  # ~14 months
        count, docids, resolver = search(
            interfaces=[ICommunity],
            content_modified=(None, coarse_datetime_repr(timeago)))
        communities = [
                {'title': community.title,
                 'url': request.resource_url(community),
                 'path': resource_path(community)}
                for community in (resolver(docid) for docid in docids)
        ]
        communities.sort(key=itemgetter('path'))

    if not box.logged_in:
        state = box.state = str(uuid.uuid4())

    return {
        'api': api,
        'menu':_menu_macro(),
        'communities': communities,
	'logged_in': logged_in,
	'state': state,
	'client_id': client.client_id,
	'authorize_url': client.authorize_url,
	'redirect_uri': request.path_url,
    }

def site_announcement_view(context, request):
    """
    Edit the text of the site announcement, which will be displayed on
    every page for every user of the site.
    """
    site = find_site(context)
    if ('submit-site-announcement' in request.params) or (
            'submit' in request.params):
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
        site.site_announcement = u''
    api = AdminTemplateAPI(context, request, 'Admin UI: Site Announcement')
    announcement = getattr(site, 'site_announcement', '')
    return dict(
        api=api,
        site_announcement=announcement,
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

        if 'send_email' in request.params or 'submit' in request.params:
            mailer = getUtility(IMailDelivery)
            group = request.params['to_group']
            users = find_users(context)
            search = ICatalogSearch(context)
            count, docids, resolver = search(interfaces=[IProfile])
            n = 0
            for docid in docids:
                profile = resolver(docid)
                if getattr(profile, 'security_state', None) == 'inactive':
                    continue
                userid = profile.__name__
                if group and not users.member_of_group(userid, group):
                    continue

                message = Message()
                if request.params['from_email'] == 'self':
                    message['From'] = from_emails[0][1]
                else:
                    message['From'] = from_emails[1][1]
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
            if has_permission(ADMINISTER, context, request):
                redirect_to = resource_url(
                    context, request, 'admin.html',
                    query=dict(status_message=status_message))
            else:
                redirect_to = resource_url(
                    find_communities(context), request, 'all_communities.html',
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

def office_dump_csv(request):
    from ZODB.utils import u64
    cursor = request.context._p_jar._storage.ex_cursor('office_dump')
    cursor.execute("""
    select get_path(state),
           state->>'modified', state->>'modified_by', state->>'title',
           state->>'mimetype'
    from newt natural join karlex
    where community_zoid = %s
      and class_name = 'karl.content.models.files.CommunityFile'
    """, (u64(find_site(request.context)['offices']._p_oid),))
    f = StringIO()
    writerow = csv.writer(f).writerow
    writerow(('File Title', 'Office',
                 'Last Updated By (User)', 'Last Updated On (Date)',
                 'File Type', 'URL'))
    for path, modified, modified_by, title, mimetype in cursor:
        office = path.split('/', 4)[2]
        writerow((title, path.split('/', 4)[2],
                  modified_by, modified,
                  mimetype, 'https://karl.soros.org'+path[:-1]))
    cursor.close()

    response = Response(f.getvalue())
    response.content_type = 'application/x-csv'
    # suggest a filename based on the report name
    response.headers.add('Content-Disposition',
                         'attachment;filename=office_dump.csv')
    return response


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

        api = AdminTemplateAPI(context, request, 'Admin UI: Upload Users')
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
            previous = resolver(iter(docids).next())
            if IInvitation.providedBy(previous):
                # This user was previously invited to join a community.  Remove
                # the invitation and carry on
                del previous.__parent__[previous.__name__]
            else:
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

def _get_redislog(registry):
    redislog = getattr(registry, 'redislog', None)
    if redislog:
        return redislog

    settings = registry.settings
    if not asbool(settings.get('redislog', 'False')):
        return

    redisconfig = dict([(k[9:], v) for k, v in settings.items()
                        if k.startswith('redislog.')])
    for intkey in ('port', 'db', 'expires'):
        if intkey in redisconfig:
            redisconfig[intkey] = int(intkey)

    from karl.redislog import RedisLog
    settings.redislog = redislog = RedisLog(**redisconfig)
    return redislog

def error_status_view(context, request):
    redislog = _get_redislog(request.registry)
    if not redislog:
        raise NotFound
    response = 'ERROR' if redislog.alarm() else 'OK'
    return Response(response, content_type='text/plain')

def redislog_view(context, request):
    redislog = _get_redislog(request.registry)
    if not redislog:
        raise NotFound

    if 'clear_alarm' in request.params:
        redislog.clear_alarm()
        query = request.params.copy()
        del query['clear_alarm']
        if query:
            kw = {'query': query}
        else:
            kw = {}
        return HTTPFound(location=request.resource_url(
            context, request.view_name, **kw))

    level = request.params.get('level')
    category = request.params.get('category')

    redis_levels = redislog.levels()
    if len(redis_levels) > 1:
        if category:
            level_params = {'category': category}
            urlkw = {'query': level_params}
        else:
            level_params = {}
            urlkw = {}
        levels = [{'name': 'All', 'current': not level,
                   'url': request.resource_url(
                       context, request.view_name, **urlkw)}]
        for choice in redis_levels:
            level_params['level'] = choice
            levels.append(
                {'name': choice,
                 'current': choice == level,
                 'url': request.resource_url(context, request.view_name,
                                             query=level_params)})
    else:
        levels = None

    redis_categories = redislog.categories()
    if len(redis_categories) > 1:
        if level:
            category_params = {'level': level}
            urlkw = {'query': category_params}
        else:
            category_params = {}
            urlkw = {}
        categories = [{'name': 'All', 'current': not category,
                       'url': request.resource_url(
                           context, request.view_name, **urlkw)}]
        for choice in redislog.categories():
            category_params['category'] = choice
            categories.append(
                {'name': choice,
                 'current': choice == category,
                 'url': request.resource_url(context, request.view_name,
                                             query=category_params)})
    else:
        categories = None

    log = [
        {'timestamp': time.asctime(time.localtime(entry.timestamp)),
         'level': entry.level,
         'category': entry.category,
         'hostname': getattr(entry, 'hostname', None), # BBB?
         'summary': entry.message.split('\n')[0],
         'details': '%s\n\n%s' % (entry.message, entry.traceback)
                    if entry.traceback else entry.message}
        for entry in redislog.iterate(
            level=level, category=category, count=100)]

    clear_params = request.params.copy()
    clear_params['clear_alarm'] = '1'
    clear_alarm_url = request.resource_url(context, request.view_name,
                                           query=clear_params)
    return {
        'api': AdminTemplateAPI(context, request),
        'menu': _menu_macro(),
        'alarm': redislog.alarm(),
        'clear_alarm_url': clear_alarm_url,
        'levels': levels,
        'level': level,
        'categories': categories,
        'category': category,
        'log': log}

def _get_postoffice_queue(context):
    zodb_uri = get_setting(context, 'zodbconn.uri.postoffice')
    queue_name = get_setting(context, 'postoffice.queue')
    if zodb_uri and queue_name:
        db = context._p_jar.db().databases['postoffice']
        return open_queue(db, queue_name)
    return None, None

def postoffice_quarantine_view(request):
    """
    See messages in postoffice quarantine.
    """
    context = request.context
    queue, closer = _get_postoffice_queue(context)
    if queue is None:
        raise NotFound

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
            location=resource_url(context, request, request.view_name)
        )

    messages = []
    for message, error in queue.get_quarantined_messages():
        po_id = message['X-Postoffice-Id']
        url = '%s/po_quarantine/%s' % (
            request.application_url, po_id
        )
        messages.append(
            dict(url=url, message_id=message['Message-Id'], po_id=po_id,
                 error=unicode(error, 'UTF-8'))
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
    if queue is None:
        raise NotFound
    if queue.count_quarantined_messages() == 0:
        return Response('OK')
    return Response('ERROR')

def postoffice_quarantined_message_view(request):
    """
    View a message in the postoffice quarantine.
    """
    queue, closer = _get_postoffice_queue(request.context)
    if queue is None:
        raise NotFound
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
    api=AdminTemplateAPI(context, request, 'Admin UI: Rename or Merge Users')
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

def debug_converters(request):
    converters = []
    for name, utility in sorted(request.registry.getUtilitiesFor(IConverter)):
        command =  getattr(utility, 'depends_on', None) or 'n/a'
        converters.append({'name': name,
                           'command': command,
                           'available': utility.isAvailable(),
                          })
    api = AdminTemplateAPI(request.context, request,
                           'Admin UI: Debug Converters')
    return {'converters': converters,
            'environ': sorted(os.environ.items()),
            'api': api,
            'menu': _menu_macro(),
           }

def restrict_access_view(context, request):
    site = find_site(context)
    access_whitelist = getattr(site, 'access_whitelist', [])
    access_blacklist = getattr(site, 'access_blacklist', [])
    restricted_notice = getattr(site, 'restricted_notice', '')
    if ('submit-access-restrictions' in request.params) or (
            'submit' in request.params):
        whitelist = request.params.get('restricted-whitelist-input', '').strip()
        whitelist = whitelist.split()
        if whitelist != access_whitelist:
            access_whitelist = site.access_whitelist = whitelist
        blacklist = request.params.get('restricted-blacklist-input', '').strip()
        blacklist = blacklist.split()
        if blacklist != access_blacklist:
            access_blacklist = site.access_blacklist = blacklist
        notice = request.params.get('restricted-notice-input', '').strip()
        if notice != restricted_notice:
            restricted_notice = site.restricted_notice = notice
    api = AdminTemplateAPI(request.context, request,
                           'Admin UI: Restrict Access')
    return {'api': api,
            'menu': _menu_macro(),
            'restricted_notice': restricted_notice,
            'access_whitelist': '\n'.join(access_whitelist),
            'access_blacklist': '\n'.join(access_blacklist),
           }

def unlock_profiles_view(context, request):
    site = find_site(context)
    if 'submit' in request.params:
        unlock = request.params.getall('unlock-profiles')
        for profile_id in unlock:
            site.login_tries[profile_id] = 8
    locked = [p[0] for p in site.login_tries.items() if p[1] < 1]
    api = AdminTemplateAPI(request.context, request,
                           'Admin UI: Unlock Accounts')
    return {'api': api,
            'locked': locked,
            'menu': _menu_macro(),
           }

def _unicode(row):
    converted = []
    for v in row:
        if isinstance(v, unicode):
            v = v.encode('utf-8')
        converted.append(v)
    return converted

def last_login_csv(context, request):
    profiles = find_profiles(context)
    f = StringIO()
    writerow = csv.writer(f).writerow
    writerow(('Login', 'Last Name', 'First Name',
                 'Email', 'Staff?', 'Last Login Date'))
    for p in profiles.values():
        # only active users
        if p.security_state != u'active':
            continue
        last_login = p.last_login_time
        last_login = last_login and last_login.strftime('%-d %b, %Y. %H:%M:%S')
        profile = (p.__name__, p.lastname, p.firstname, p.email,
                   is_staff(p, None) and 'Yes' or 'No', last_login)
        writerow(_unicode(profile))

    response = Response(f.getvalue())
    response.content_type = 'application/x-csv'
    response.headers.add('Content-Disposition',
                         'attachment;filename=last_login.csv')
    return response
