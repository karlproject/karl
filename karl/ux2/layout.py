from bottlecap.layout import LayoutManager as BaseLayoutManager


class LayoutManager(BaseLayoutManager):

    @property
    def global_nav_menus(self):
        menu_items = [
            dict(title="Intranet", selected=None),
            dict(title="Communities", selected="selected"),
            dict(title="People", selected=None),
            dict(title="Calendar", selected=None),
            dict(title="Explore", selected=None),
            ]
        return menu_items


def global_nav(context, request):
    return {}
