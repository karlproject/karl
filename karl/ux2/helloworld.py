from karl.views.api import TemplateAPI


def helloworld_view(context, request):
    return {"api": TemplateAPI(context, request),
            "project": "Some Project"}
