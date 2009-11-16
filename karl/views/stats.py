from webob import Response
import sys
import os

from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.chameleon_zpt import get_template
from repoze.bfg.security import has_permission
from repoze.bfg.security import effective_principals
from repoze.bfg.traversal import model_path
from repoze.bfg.traversal import find_interface
from repoze.bfg.url import model_url
from repoze.workflow import get_workflow
from repoze.enformed import FormSchema
from karl.views.api import TemplateAPI

def stats(context, request):
    me = sys.argv[0]
    me = os.path.abspath(me)
    sandbox = os.path.dirname(os.path.dirname(me))
    outfile_path = os.path.join(sandbox, 'var/stats/', 'stats.csv')
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

    
    return Response(resp_out)
