from karl.utils import find_intranets


def global_nav(context, request):
    layout = request.layout_manager.layout
    site = layout.site
    menu_items = [
        dict(title="Communities",
             url=request.resource_url(site, 'communities'),
             selected='selected'),
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


def personal_tools(context, request):
    return {}


def search(context, request):
    return {}


def context_tools(context, request):
    return {}


def actions_menu(context, request, actions):
    return {'actions': actions}


def column_one(context, request):
    return {}
