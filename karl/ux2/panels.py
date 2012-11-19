import os
from cgi import escape
import json

from pyramid.encode import urlencode
from pyramid.security import authenticated_userid
from pyramid.security import effective_principals
from pyramid.security import has_permission
from pyramid.traversal import resource_path
from pyramid.url import resource_url

from karl.content.views.utils import fetch_attachments
from karl.models.interfaces import ICatalogSearch
from karl.models.interfaces import ICommunityContent
from karl.models.interfaces import IGridEntryInfo
from karl.utilities.image import thumb_url
from karl.utilities.interfaces import IKarlDates
from karl.utils import find_intranets
from karl.utils import find_profiles
from karl.utils import find_community
from karl.utils import find_chatter
from karl.utils import find_site
from karl.utils import get_setting
from karl.utils import asbool
from karl.views.people import PROFILE_THUMB_SIZE
from karl.views.utils import get_user_home
from karl.views.utils import make_name
from karl.views.utils import get_static_url
from karl.views.chatter import CHATTER_THUMB_SIZE


PROFILE_ICON_SIZE = (25, 25)
EMPTY_CONTEXT = {}


def generic_panel(context, request):
    return {}


def column_one(context, request):
    layout_manager = request.layout_manager
    layout = layout_manager.layout
    render = layout_manager.render_panel
    if layout.portlets:
        return '\n'.join(
            [render(name, *args, **kw)
             for name, args, kw in layout.portlets])
    return ''


def global_nav(context, request):

    def menu_item(title, url, id=None, count=None, secondary=None):
        if id is None:
            id = make_name(EMPTY_CONTEXT, title)
        selected = request.resource_url(context).startswith(url)
        if secondary is not None and not selected:
            selected = request.resource_url(context).startswith(secondary)
        item = dict(title=title,
                    url=url,
                    id=id,
                    selected=selected and 'selected' or None)
        if count is not None:
            item['count'] = count
        return item

    layout = request.layout_manager.layout
    site = layout.site
    menu_items = [
        menu_item("Communities", request.resource_url(site, 'communities')),
        menu_item("People", layout.people_url, secondary=layout.profiles_url),
        menu_item("Feeds", request.resource_url(site, 'contentfeeds.html')),
        ]
    intranets = find_intranets(site)
    if layout.current_intranet is not None:
        menu_items.insert(0, menu_item("Intranet",
             request.resource_url(intranets)))
    if layout.should_show_calendar_tab:
        menu_items.append(menu_item("Calendar",
             request.resource_url(site, 'offices', 'calendar')))
    if layout.user_is_staff:
        menu_items.append(menu_item("Tags",
             request.resource_url(site, 'tagcloud.html'), id='tagcloud'))
    chatter = find_chatter(site)
    menu_items.append(menu_item("Chatter", request.resource_url(chatter)))
    # XXX Radar is disabled for the time.
    ## menu_items.append(menu_item("Radar", "#", count="7"))
    overflow_menu = []
    #if layout.user_is_staff:
    #    overflow_menu.append(menu_item("Tags",
    #         request.resource_url(site, 'tagcloud.html'), id='tagcloud'))
    return {'nav_menu': menu_items, 'overflow_menu': overflow_menu}


def context_tools(context, request, tools=None):
    overflow_menu = []
    community = find_community(context)
    if community:
        url = request.resource_url(community, 'tagcloud.html')
        selected = 'tagcloud.html' in request.path_url
        tools.append(dict(title="Tags",
                                  url=url,
                                  selected=selected,
                                  id='tagcloud'))
    return {'tools': tools}


def actions_menu(context, request, actions):
    if not actions:
        return '' # short circuit renderer

    # Allow views to pass in UX2 action menu.  The menu will be a dict.
    if isinstance(actions, dict):
        return actions

    # Backwards compatability layer.  Attempt to convert old style UX1 actions
    # into newer menu structure.
    converted = []
    addables = []
    overflow_menu = []
    for title, url in actions:
        if title.startswith('Add '):
            addables.append((title, url))
        # very difficult to convert a simple tuple structure into a full
        # featured ux2 menu. Let's add the overflow menu if there's a manage
        # option and put all remaining options after that there.
        elif title.startswith('Manage ') or overflow_menu != []:
            overflow_menu.append({'title': title, 'url': url})
        else:
            converted.append({'title': title, 'url': url})

    if len(addables) > 2:
        converted.insert(0, {
            'title': 'Add',
            'subactions': [{'title': title[4:], 'url': url}
                            for title, url in addables]})
    else:
        converted = [{'title': title, 'url': url}
                     for title, url in addables] + converted

    menu = {'actions': converted}

    if len(overflow_menu) > 0:
        menu['overflow_menu'] = overflow_menu

    return menu


def personal_tools(context, request):
    profiles = find_profiles(context)
    name = authenticated_userid(request)
    profile = profiles[name]
    photo = profile.get('photo')
    if photo is not None:
        icon_url = thumb_url(photo, request, PROFILE_ICON_SIZE)
    else:
        icon_url = request.static_url('karl.views:static/ux2/img/person.png')
    profile_url = request.resource_url(profile)
    return {'profile_url': profile_url,
            'icon_url': icon_url}
            


def status_message(context, request):
    message = request.params.get('status_message')
    if message:
        return '<div class="notification info">%s</div>' % escape(message)
    return ''


def error_message(context, request):
    message = request.layout_manager.layout.error_message
    if message:
        return '<div class="portalErrorMessage">%s</div>' % escape(message)
    return ''


def global_logo(context, request):
    home_context, home_path = get_user_home(context, request)
    return {'logo_title': request.registry.settings.get('system_name', 'KARL'),
            'logo_href': request.resource_url(home_context, *home_path)}

def my_communities(context, request, my_communities, preferred_communities,
                   communities = None):
    return {
        'my_communities': my_communities,
        'preferred_communities': preferred_communities,
        'communities': communities}


def my_tags(context, request, profile, tags):
    profiles = find_profiles(context)
    name = authenticated_userid(request)
    current_profile = profiles[name]
    if current_profile == profile:
        mine = True
    else:
        mine = False
    return {'tags': tags,
            'mine': mine,
            'firstname': profile.firstname}


# --
# XXX This used to belong to "api". Now, we need it from the footer
# panel. In case the same info is needed from other panels, there
# is a choice to reuse this method from that panel, or, if generic
# enough, move it to "layout".

from pyramid.url import resource_url
from pyramid.traversal import quote_path_segment
from repoze.lemonade.content import get_content_type

from karl.models.interfaces import ICommunity


def intranets_info(context, request):
    """Get information for the footer and intranets listing"""
    intranets_info = []
    intranets = find_intranets(context)
    if intranets:
        intranets_url = resource_url(intranets, request)
        for name, entry in intranets.items():
            try:
                content_iface = get_content_type(entry)
            except ValueError:
                continue
            if content_iface == ICommunity:
                if not has_permission('view', entry, request):
                    continue
                href = '%s%s/' % (intranets_url, quote_path_segment(name))
                intranets_info.append({
                        'title': entry.title,
                        'intranet_href': href,
                        'edit_href': href + '/edit_intranet.html',
                        })
        # Sort the list
        def intranet_sort(x, y):
            if x['title'] > y['title']:
                return 1
            else:
                return -1
        intranets_info.sort(intranet_sort)
    return intranets_info


def footer(context, request):
    return {
        'intranets_info': intranets_info(context, request),
        }


def search(context, request):
    scope_options = []
    scope_options.append(dict(
        path = '',
        name = 'all KARL',
        label = 'all KARL',
        selected = True,
        ))
    # We add a second option, in case, context is inside a community.
    community = find_community(context)
    if community:
        # We are in a community!
        scope_options.append(dict(
            path = resource_path(community),
            name = 'this community',
            label = community.title,
        ))

    return {
        'scope_options': scope_options,
        }


def attachments(context, request, other_context=None):
    if other_context:
        context = other_context
    has_attachments = 'attachments' in context and context['attachments']
    get_attachments = getattr(context, 'get_attachments', None)
    if not get_attachments and not has_attachments:
        return ''
    folder = has_attachments or get_attachments()
    return {'attachments': fetch_attachments(folder, request)}


def comments(context, request):
    profiles = find_profiles(context)
    karldates = request.registry.getUtility(IKarlDates)
    comments = []
    for comment in context['comments'].values():
        profile = profiles.get(comment.creator)
        author_name = profile.title
        author_url = resource_url(profile, request)

        newc = {}
        newc['id'] = comment.__name__
        if has_permission('edit', comment, request):
            newc['edit_url'] = resource_url(comment, request, 'edit.html')
        else:
            newc['edit_url'] = None

        if has_permission('delete', comment, request):
            newc['delete_url'] = resource_url(comment, request, 'delete.html')
        else:
            newc['delete_url'] = None

        if has_permission('administer', comment, request):
            newc['advanced_url'] = resource_url(comment, request, 'advanced.html')
        else:
            newc['advanced_url'] = None

        # Display portrait
        photo = profile.get('photo')
        if photo is not None:
            photo_url = thumb_url(photo, request, PROFILE_THUMB_SIZE)
        else:
            photo_url = request.static_url(
                "karl.views:static/images/defaultUser.gif")
        newc["portrait_url"] = photo_url

        newc['author_url'] = author_url
        newc['author_name'] = author_name

        newc['date'] = karldates(comment.created, 'longform')
        newc['timestamp'] = comment.created
        newc['text'] = comment.text

        # Fetch the attachments info
        newc['attachments'] = fetch_attachments(comment, request)
        comments.append(newc)
    comments.sort(key=lambda c: c['timestamp'])
    return {'comments': comments}


def tagbox(context, request,
        html_id=None,
        html_class='',
        options={}):
    """Renders the tagbox

    html_id, html_class will be added as attributes of the top HTML node.

    If "prevals" option is not specified, then head_data.panel_data.tagbox
    will be used as initial data. Anything else can be overwritten from
    the panel parameters as well, if nothing is specified we will get a portlet tagbox.
    """

    if html_id is None:
        layout = request.layout_manager.layout
        html_id = layout.html_id()

    return {
        'html_id': html_id,
        'html_class': html_class,
        # these are used by the template
        'widget_options': options,
        }


def chatter_show_only(context, request):
    return {}


def chatter_search(context, request):
    return {}


def chatter_user_search(context, request):
    return {}


def chatter_post(context, request, chatter_form_url, creator=None,
                 reply=False, private=False, recipient=None):
    return {'chatter_form_url': chatter_form_url,
            'creator': creator,
            'private': private,
            'recipient': recipient,
            'reply': reply}


def chatter_post_display(context, request, chatter_form_url, post,
                         recursive=True):
    return {'chatter_form_url': chatter_form_url,
            'post': post,
            'recursive': recursive}


def chatter_user_info(context, request, userid=None):
    chatter = find_chatter(context)
    chatter_url = resource_url(chatter, request)
    profiles = find_profiles(context)
    if userid is None:
        userid = request.GET.get('userid')
    if userid is None:
        userid = authenticated_userid(request)
    profile = profiles.get(userid)
    profile_url = profile and resource_url(profile, request) or None
    photo = profile and profile.get('photo') or None
    if photo is not None:
        photo_url = thumb_url(photo, request, CHATTER_THUMB_SIZE)
    else:
        photo_url = get_static_url(request) + "/images/defaultUser.gif"
    posts = sum(1 for p in chatter.recentWithCreators(*[userid]))
    following = sum(1 for u in chatter.listFollowed(userid))
    followers = sum(1 for u in chatter.listFollowing(userid))
    return {'creator': getattr(profile, 'title', 'anonymous'),
            'creator_url': '%s%s' % (chatter_url, userid),
            'creator_profile_url': profile_url,
            'creator_image_url': photo_url,
            'creator_userid': userid,
            'chatter_url': chatter_url,
            'posts': posts,
            'following': following,
            'followers': followers}


def quip_search(context, request):
    return {}


def chatter_tag_search(context, request):
    return {}


def chatter_tag_info(context, request, followed_tags, tag_list, tag=None):
    limit = 40
    chatter = find_chatter(context)
    chatter_url = resource_url(chatter, request)
    return {'tag_list': tag_list[:limit],
            'followed_tags': followed_tags,
            'this_tag': tag,
            'chatter_url': chatter_url}


def followers(context, request):
    return {}


def discover(context, request):
    return {}


def admin_menu(context, request):
    admin_settings = {}
    site = find_site(context)
    settings = request.registry.settings
    syslog_view = get_setting(context, 'syslog_view', None)
    admin_settings['syslog_view_enabled'] = syslog_view != None
    admin_settings['has_logs'] = not not get_setting(context, 'logs_view', None)
    admin_settings['redislog'] = asbool(settings.get('redislog', 'False'))
    admin_settings['can_administer'] = has_permission('administer', site, request)
    admin_settings['can_email'] = has_permission('email', site, request)
    statistics_folder = get_setting(context, 'statistics_folder', None)
    if statistics_folder is not None and os.path.exists(statistics_folder):
        csv_files = [fn for fn in os.listdir(statistics_folder)
                    if fn.endswith('.csv')]
        admin_settings['statistics_view_enabled'] = not not csv_files
    else:
        admin_settings['statistics_view_enabled'] = False
    admin_settings['quarantine_url'] = ('%s/po_quarantine.html' %
                            request.application_url)
    site = find_site(context)
    if 'offices' in site:
        admin_settings['offices_url'] = resource_url(site['offices'], request)
    else:
        admin_settings['offices_url'] = None
    admin_settings['has_mailin'] = (
        get_setting(context, 'zodbconn.uri.postoffice') and
        get_setting(context, 'postoffice.queue'))
    return admin_settings


def follow_info(context, request, creators):
    return {'creators': creators,
            'chatter_url': request.resource_url(context)}


def wiki_lock(context, request, lock_info):
    return {'lock_info': lock_info}


def searchresults(context, request, r, doc, result_display):
    return {'r': r, 'result_display': result_display, 'doc': doc}


def site_announcement(context, request):
    site = find_site(context)
    body = None
    if hasattr(site, 'site_announcement'):
        body = site.site_announcement
    return dict(
        show=True if body else False,
        body=body,
    )


def grid_header(context, request, letters=None, filters=None, formats=None,
                actions=None):
    return {
        'letters': letters,
        'filters': filters,
        'formats': formats,
        'actions': actions}


def grid_footer(context, request, batch):
    # Pagination
    batch_size = batch.get('batch_size', 0)
    if batch_size == 0:
        n_pages = 0
        batch['total'] = 0
    else:
        n_pages = (batch['total'] - 1) / batch_size + 1
    if n_pages <= 1:
        batch['pagination'] = False
        return batch

    url = request.path_url
    def page_url(page):
        params = request.GET.copy()
        params['batch_start'] = str(page * batch_size)
        return '%s?%s' % (url, urlencode(params))

    batch['pagination'] = True
    current = batch['batch_start'] / batch['batch_size']
    if current > 0:
        batch['prev_url'] = page_url(current - 1)
    else:
        batch['prev_url'] = None
    if current + 1 < n_pages:
        batch['next_url'] = page_url(current + 1)
    else:
        batch['next_url'] = None
    pages = []
    for i in xrange(n_pages):
        ellipsis = i != 0 and i != n_pages - 1 and abs(current - i) > 3
        if ellipsis:
            if pages[-1]['name'] != 'ellipsis':
                pages.append({
                    'name': 'ellipsis',
                    'title': '...',
                    'url': None,
                    'selected': False})
        else:
            title = '%d' % (i + 1)
            pages.append({
                'name': title,
                'title': title,
                'url': page_url(i),
                'selected': i == current})

    batch['pages'] = pages
    return batch


def extra_css(context, request):
    layout = request.layout_manager.layout
    static_url = request.static_url
    css = []
    for spec in layout.extra_css:
        # We allow spec to be an absolute url, in which case
        # we "just use it".
        if not (spec.startswith('http://') or spec.startswith('https://')):
            spec = static_url(spec)
        css.append('\t\t<link rel="stylesheet" href="%s" />' % spec)
    return '\n'.join(css)


def extra_js(context, request, defer=True):
    layout = request.layout_manager.layout
    static_url = request.static_url
    js = []
    for spec in layout.extra_js:
        # We allow spec to be an absolute url, in which case
        # we "just use it".
        if not (spec.startswith('http://') or spec.startswith('https://')):
            spec = static_url(spec)
        js.append('\t\t<script src="%s" %s></script>' % (spec, 'defer' if defer else ''))
    return '\n'.join(js)


def extra_css_head(context, request):
    layout = request.layout_manager.layout
    static_url = request.static_url
    css = []
    for spec in layout.extra_css_head:
        # We allow spec to be an absolute url, in which case
        # we "just use it".
        if not (spec.startswith('http://') or spec.startswith('https://')):
            spec = static_url(spec)
        css.append('\t\t<link rel="stylesheet" href="%s" />' % spec)
    return '\n'.join(css)


def extra_js_head(context, request):
    layout = request.layout_manager.layout
    static_url = request.static_url
    js = []
    for spec in layout.extra_js_head:
        # We allow spec to be an absolute url, in which case
        # we "just use it".
        if not (spec.startswith('http://') or spec.startswith('https://')):
            spec = static_url(spec)
        # XXX We make it all non-defer. Revise and provide a parameter,
        # XXX if it makes sense!
        defer = False
        js.append('\t\t<script src="%s" %s></script>' % (spec, 'defer' if defer else ''))
    return '\n'.join(js)


def related_tags(context, request, related):
    def tagurl(tag):
        return request.resource_url(context, 'showtag', tag)
    return {'related': related,
            'tagurl': tagurl}


def recent_activity(context, request):
    community = find_community(context)
    if not community:
        return ''

    registry = request.registry
    community_path = resource_path(community)
    search = registry.getAdapter(context, ICatalogSearch)
    principals = effective_principals(request)
    recent_items = []
    num, docids, resolver = search(
        limit=10,
        path={'query': community_path},
        allowed={'query': principals, 'operator': 'or'},
        sort_index='modified_date',
        reverse=True,
        interfaces=[ICommunityContent],
        )
    models = filter(None, map(resolver, docids))
    for model in models:
        adapted = registry.getMultiAdapter((model, request), IGridEntryInfo)
        recent_items.append(adapted)

    return {'recent_items': recent_items}


def backto(context, request, backto):
    return {'backto': backto}


def gridbox(context, request,
        html_id=None,
        html_class='',
        widget_options={}):
    """Renders a gridbox component

    html_id, html_class will be added as attributes of the top HTML node.
    widget_options is passed to the slickgrid widget, after sensible
    defaults applied from this view and from the template (for cross-wiring).
    """

    layout = request.layout_manager.layout

    # Select client component
    layout.select_client_component('slickgrid')

    if html_id is None:
        html_id = layout.html_id()

    default_widget_options = {
        'columns': [
            {'field': 'sel', 'width': 50},
            {'field': 'filetype', 'name': 'Type', 'width': 80},
            {'field': 'title', 'name': 'Title', 'width': 610},
            {'field': 'modified', 'name': 'Last Modified', 'width': 200},
            ],
        'checkboxSelectColumn': True,
        #'minimumLoad': 250,   # The ajax will fetch at least this many rows
        'minimumLoad': 50,   # The ajax will fetch at least this many rows
        }
    default_widget_options.update(widget_options)
    widget_options = default_widget_options

    return {
        'html_id': html_id,
        'html_class': html_class,
        'widget_options': json.dumps(widget_options),
        'delete_url': request.resource_url(context, 'delete_files.json'),
        'moveto_url': request.resource_url(context, 'move_files.json'),
        'download_url': request.resource_url(context, 'download_zipped'),
        }


def grid(context, request,
        html_id=None,
        html_class='',
        widget_options={}):
    """Renders a popper grid component

    html_id, html_class will be added as attributes of the top HTML node.
    widget_options is passed to the slickgrid widget, after sensible
    defaults applied from this view and from the template (for cross-wiring).

    This is used from the people grid
    """

    layout = request.layout_manager.layout

    # Select client component
    layout.select_client_component('slickgrid')

    if html_id is None:
        html_id = layout.html_id()

    default_widget_options = {
        'minimumLoad': 50,   # The ajax will fetch at least this many rows
        }
    default_widget_options.update(widget_options)
    widget_options = default_widget_options

    return {
        'html_id': html_id,
        'html_class': html_class,
        'widget_options': json.dumps(widget_options),
        }


def cal_header(context, request,
        html_id=None,
        html_class='',
        options={}):
    """Renders the calendar header toolbar

    html_id, html_class will be added as attributes of the top HTML node.
    options['toolbar'] will be passed to the javascript widget of the toolbar.
    (most notably 'selection' is needed in there.)
    """

    if html_id is None:
        layout = request.layout_manager.layout
        html_id = layout.html_id()

    # This is just a visual speedup. The javascript of the toolbar
    # will initialize the labels. By ghosting these initial
    # values it is a quicker experience for the user.
    toolbar_selection_labels = dict(options['toolbar']['selection'])
    toolbar_selection_labels['month'] = ['Jan', 'Feb', 'Mar', 'Apr', 'May',
        'Jun', 'Jul', 'Aug', 'Sep',
        'Oct', 'Nov', 'Dec'][toolbar_selection_labels['month'] - 1]

    return {
        'html_id': html_id,
        'html_class': html_class,
        'toolbar_options': json.dumps(options['toolbar']),
        # these are used by the template
        'setup_url': options['setup_url'],
        'calendar': options['calendar'],
        'selected_layer_title': options['selected_layer_title'],
        'layers': options['layers'],
        'may_create': options['may_create'],
        'mailto_create_event_href': options['mailto_create_event_href'],
        # some more helpers
        'toolbar_selection_labels': toolbar_selection_labels,
        }


def cal_footer(context, request,
        html_id=None,
        html_class='',
        options={}):
    """Renders the calendar footer

    html_id, html_class will be added as attributes of the top HTML node.
    """

    if html_id is None:
        layout = request.layout_manager.layout
        html_id = layout.html_id()

    return {
        'html_id': html_id,
        'html_class': html_class,
        # these are used by the template
        'calendar': options['calendar'],
        }

