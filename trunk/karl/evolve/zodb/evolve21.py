from karl.models.contentfeeds import SiteEvents

def evolve(context):
    if getattr(context, 'events', None) is None:
        print "Adding 'events' to root"
        context.events = SiteEvents()
    # Fix up tag objects to store their own ID.
    for tag_id, tag_obj in context.tags._tagid_to_obj.items():
        tag_obj._id = tag_id
    # Fix up any existing events to store profile_url
    for gen, index, mapping in context.events:
        if 'profile_url' not in mapping:
            profile_url = '/'.join(mapping['thumbnail'].split('/')[:-1])
            mapping['profile_url'] = profile_url
