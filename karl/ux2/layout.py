from karl.views.api import TemplateAPI


class Layout(TemplateAPI):

    def __init__(self, context, request):
        super(Layout, self).__init__(context, request)
        self.popper_static_url = request.static_url(
            'bottlecap.layouts.popper:static/')

