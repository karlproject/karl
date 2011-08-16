from pyramid.response import Response

def ok(context, request):
    return Response('OK')
