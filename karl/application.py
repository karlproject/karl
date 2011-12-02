from karl.ux2.layout import LayoutManager


def configure_karl(config):
    config.include('bottlecap')
    config.add_bc_layout({'site': 'karl.ux2:templates/site_layout.pt'})
    config.add_bc_layoutmanager_factory(LayoutManager)

