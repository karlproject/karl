from repoze.bfg.chameleon_zpt import renderer_factory

from webob import Response

def render_form_to_response(template_path, schema, fieldvalues,
                            form_id='contentform',
                            rendering_method='html', **kw):
    """ Render a ``chameleon.zpt`` form template at the
    package-relative path (may also be absolute) using the kwargs in
    ``*kw`` as top-level names, the schema, and the fieldvalues, and
    return a Webob response."""
    renderer = renderer_factory(template_path)
    body = renderer(kw, {})
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
    
