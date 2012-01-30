from cgi import escape
from pyramid.security import authenticated_userid
from karl.utils import find_intranets
from karl.utils import find_profiles
from karl.views.utils import get_user_home


def global_nav(context, request):
    layout = request.layout_manager.layout
    site = layout.site
    menu_items = [
        dict(title="Communities",
             url=request.resource_url(site, 'communities'),
             selected=None),
        dict(title="People",
             url=layout.people_url,
             selected=None),
        dict(title="Feeds",
             url=request.resource_url(site, 'contentfeeds.html'),
             selected=None),
        ]
    intranets = find_intranets(site)
    if layout.current_intranet is not None:
        menu_items.insert(0, dict(title="Intranet",
             url=request.resource_url(intranets),
             selected=None))
    if layout.should_show_calendar_tab:
        menu_items.append(dict(title="Calendar",
             url=request.resource_url(site, 'offices', 'calendar'),
             selected=None))
    if layout.user_is_staff:
        menu_items.append(dict(title="Tags",
             url=request.resource_url(site, 'tagcloud.html'),
             selected=None))
    return {'nav_menu': menu_items}


def actions_menu(context, request, actions):
    # Karl has traditionally used a list of tuples (title, view_name) to
    # represent actions.  Popper layout expects a list of dicts.  Actions
    # are passed to the renderer by individual views which then pass them
    # to the panel.
    if not actions:
        return '' # short circuit renderer

    converted = []
    addables = []
    for title, url in actions:
        if title.startswith('Add '):
            addables.append((title, url))
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

    return {'actions': converted}


def personal_tools(context, request):
    profiles = find_profiles(context)
    name = authenticated_userid(request)
    return {'profile_name': profiles[name].title}


def status_message(context, request):
    message = request.params.get('status_message')
    if message:
        return '<div class="portalMessage">%s</div>' % escape(message)
    return ''


def global_logo(context, request):
    home_context, home_path = get_user_home(context, request)
    return {'logo_title': request.registry.settings.get('system_name', 'KARL'),
            'logo_href': request.resource_url(home_context, *home_path)}

def my_communities(context, request, my_communities, preferred_communities):
    return {
        'my_communities': my_communities,
        'preferred_communities': preferred_communities}



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
            href = '%s%s/' % (intranets_url, quote_path_segment(name))
            if content_iface == ICommunity:
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


def skinswitcher(context, request):
    using_ux2 = request.cookies.get('ux2') == 'true'
    return {
        'skinswitcher': dict(value='false', label='LEGACY') \
            if using_ux2 \
            else dict(value='true', label='UX2'),
        }