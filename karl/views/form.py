from repoze.bfg.settings import get_settings
from repoze.bfg.chameleon_zpt import ZPTTemplateRenderer
from repoze.bfg.templating import renderer_from_cache

from webob import Response

def render_form_to_response(template_path, schema, fieldvalues,
                            form_id='contentform',
                            rendering_method='html', **kw):
    """ Render a ``chameleon.zpt`` form template at the
    package-relative path (may also be absolute) using the kwargs in
    ``*kw`` as top-level names, the schema, and the fieldvalues, and
    return a Webob response."""
    settings = get_settings()
    auto_reload = settings and 'reload_templates' in settings
    renderer = renderer_from_cache(template_path, ZPTTemplateRenderer,
                                   auto_reload=auto_reload, level=3)
    body = renderer(**kw)
    if body: 
        rendered = schema.render(body, fieldvalues, form_id, rendering_method)
    else:
        # for unit testing
        rendered = ''
        renderer.fieldvalues = fieldvalues
        renderer.form_body = body
        renderer.form_id = form_id
        renderer.rendering_method = rendering_method
    return Response(rendered)
    
