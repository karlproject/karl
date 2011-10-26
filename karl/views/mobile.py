# Views in support of jquerymobile

from karl.views.api import TemplateAPI

def home(context, request):
    api = TemplateAPI(context, request, 'Mobile')
    return {'api': api}
