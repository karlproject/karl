from paste.script.templates import Template

from paste.util.template import paste_script_template_renderer

class KARLProjectTemplate(Template):
    _template_dir = 'paster_templates/karl_project'
    summary = 'KARL customization project'
    template_renderer = staticmethod(paste_script_template_renderer)

