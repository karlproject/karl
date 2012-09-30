#

import sys
import os
import json
import deform
from pkg_resources import resource_filename

def _concat_path(fname, *rnames):
    return os.path.join(os.path.dirname(fname), *rnames)

def module_path(mod, *rnames):
    return _concat_path(mod.__file__, *rnames)

this_module = sys.modules[__name__]

deform_templates = resource_filename('deform', 'templates')
search_path = (module_path(this_module, 'templates'), deform_templates)
renderer = deform.ZPTRendererFactory(search_path)

#class FormWidget(deform.widget.FormWidget):
#    item_template = 'mapping_item'

class Form(deform.Form):
    """Custom form used by KARL UX2"""

    def __init__(self, schema, action='', method='POST', buttons=(),
                 formid='deform', use_ajax=False, ajax_options='{}', **kw):
        # Use our own "renderer", making sure that our templates directory is scanned
        # before the default deform templates.
        kw = dict(kw)
        kw.update(renderer=renderer)
        deform.Form.__init__(self, schema, action=action, method=method, buttons=buttons,
                 formid=formid, use_ajax=use_ajax, ajax_options=ajax_options, **kw)
        # override the formwidget with ours
        ##self.widget = FormWidget()

    def dict_to_json(self, d):
        return json.dumps(d.asdict())
