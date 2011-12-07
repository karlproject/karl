from karl.ux2.layout import LayoutManager


def configure_karl(config, load_zcml=True):
    config.include('bottlecap')
    config.add_bc_layout({'site': 'karl.ux2:templates/site_layout.pt'})
    config.add_bc_layoutmanager_factory(LayoutManager)

    if load_zcml:
        config.hook_zca()
        config.include('pyramid_zcml')
        config.load_zcml('standalone.zcml')
