from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response


def switch_ui(request):
    using_ux2 = request.cookies.get('ux2_kachoo') == 'true'
    if request.method == 'POST':
        response = HTTPFound(request.application_url)
        if using_ux2:
            response.set_cookie('ux2_kachoo', 'false')
        else:
            response.set_cookie('ux2_kachoo', 'true')
        return response

    if using_ux2:
        button_text = 'Switch to Classic UI'
    else:
        button_text = 'Switch to New and Improved UI'
    return Response(
        '<html><head><title>Karl: Change UI</title></head>'
        '<body><form method="POST"><input type="submit" value="%s"/></form>'
        '</body></html>' % button_text, content_type='text/html')
