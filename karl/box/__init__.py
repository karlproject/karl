
def includeme(config):
    config.add_route('archive_to_box', '/arc2box/*traverse')
    config.scan('.')
