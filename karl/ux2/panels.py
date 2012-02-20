from cgi import escape

from pyramid.security import authenticated_userid
from pyramid.security import has_permission
from pyramid.traversal import resource_path

from karl.content.views.utils import fetch_attachments
from karl.utilities.image import thumb_url
from karl.utilities.interfaces import IKarlDates
from karl.utils import find_intranets
from karl.utils import find_profiles
from karl.utils import find_community
from karl.views.people import PROFILE_THUMB_SIZE
from karl.views.utils import get_user_home

PROFILE_ICON_SIZE = (15, 15)

def global_nav(context, request):

    def menu_item(title, url):
        selected = request.resource_url(context).startswith(url)
        return dict(title=title,
                    url=url,
                    selected=selected and 'selected' or None)

    layout = request.layout_manager.layout
    site = layout.site
    menu_items = [
        menu_item("Communities", request.resource_url(site, 'communities')),
        menu_item("People", layout.people_url),
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
             request.resource_url(site, 'tagcloud.html')))
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
    profile = profiles[name]
    photo = profile.get('photo')
    if photo is not None:
        icon_url = thumb_url(photo, request, PROFILE_ICON_SIZE)
    else:
        icon_url = request.static_url('karl.views:static/img/person.png')
    profile_url = request.resource_url(profile)
    logout_url = "%s/logout.html" % request.application_url
    return {'profile_name': profile.title,
            'profile_url': profile_url,
            'icon_url': icon_url,
            'logout_url': logout_url}


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
    get_attachments = getattr(context, 'get_attachments', None)
    if not get_attachments:
        return ''
    folder = get_attachments()
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

