
def add_location_header(event):
    request = event.request
    response = event.response
    if request.method == 'GET' and response.status_int == 200:
        response.headers['X-Karl-Location'] = request.url
