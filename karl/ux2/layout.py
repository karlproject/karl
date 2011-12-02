from bottlecap.layout import LayoutManager as BaseLayoutManager


class LayoutManager(BaseLayoutManager):

    @property
    def my_global_nav_menus(self):
        menu_items = [
            dict(title="Item 1", selected='selected'),
            dict(title="Item 2", selected=None),
            dict(title="Item 3", selected=None),
            dict(title="Item 4", selected=None),
            dict(title="Item 5", selected=None),
            ]
        return menu_items


def global_nav(context, request):
    return {}
