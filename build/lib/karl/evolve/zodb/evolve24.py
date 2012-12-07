from karl.utils import find_tags

def evolve(root):
    tags = find_tags(root)
    dupe_ids = []
    print "Searching for duplicate tags..."
    seen_tags = set()
    for id, tag in tags._tagid_to_obj.items():
        if tag in seen_tags:
            dupe_ids.append(id)
        else:
            seen_tags.add(tag)

    tags._delTags(dupe_ids)
    print "Removed %d duplicate tags" % len(dupe_ids)