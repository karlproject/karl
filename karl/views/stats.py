from webob import Response
import sys
import os

from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.exceptions import NotFound
from karl.views.api import TemplateAPI

def stats(context, request):
    """
    This appears to no longer be in use.  If we can't confirm someone is using
    it after some period of time we shoudl probably get rid of it.
    --rossi 5/5/2011
    """
    me = sys.argv[0]
    me = os.path.abspath(me)
    sandbox = os.path.dirname(os.path.dirname(me))
    outfile_path = os.path.join(sandbox, 'var/stats/', 'stats.csv')
    if not os.path.exists(outfile_path):
        raise NotFound
    f = open(outfile_path, 'r')
    lines = f.readlines()
    resp_out = ""
    line_arrays = []
    for line in lines:
        resp_out = resp_out + line + "<br/>"
        line2 = line
        myarr = line2.split(",")
        line_arrays.append(myarr)

    page_title = 'Admin Statistics'
    api = TemplateAPI(context, request, page_title)

    return render_template_to_response(
        'templates/stats.pt',
        api = api,
        stats = resp_out,
        comms = line_arrays,
        )
