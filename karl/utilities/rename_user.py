from repoze.bfg.traversal import model_path

from karl.models.interfaces import ICatalogSearch
from karl.utils import find_catalog
from karl.utils import find_profiles
from karl.utils import find_users

def rename_user(context, old_name, new_name, merge=False, out=None):
    """
    Renames a user with the given userid to a new userid. If `merge` is `True`
    a user is expected to already exist with userid `new_name`. Moves all
    content and group memberships from old user to new user before removing the
    old user.
    """
    profiles = find_profiles(context)
    users = find_users(context)

    old_user = users.get_by_id(old_name)
    if old_user is None:
        raise ValueError("No such user: %s" % old_user)

    if old_name not in profiles:
        raise ValueError("No such profile: %s" % old_user)

    if merge:
        if users.get_by_id(new_name) is None:
            raise ValueError("No such user: %s" % new_name)
        if new_name not in profiles:
            raise ValueError("No such profile: %s" % new_name)

        if out is not None:
            print >>out, "Renaming user from %s to %s" % (old_name, new_name)

        for group in old_user['groups']:
            if not users.member_of_group(new_name, group):
                users.add_user_to_group(new_name, group)
        users.remove(old_name)
        del profiles[old_name]

    else:
        if users.get_by_id(new_name) is not None:
            raise ValueError("User already exists: %s" % new_name)
        if new_name in profiles:
            raise ValueError("Profile already exists: %s" % new_name)

        if out is not None:
            print >>out, "Merging user %s to %s" % (old_name, new_name)

        users.add(new_name, new_name, old_user['password'],
                  old_user['groups'], encrypted=True)
        users.remove(old_name)

        profile = profiles[old_name]
        del profiles[old_name]
        profiles[new_name] = profile

    catalog = find_catalog(context)
    search = ICatalogSearch(context)

    index = catalog['creator']
    count, docids, resolver = search(creator=old_name)
    for docid in docids:
        doc = resolver(docid)
        if out is not None:
            print >>out, "Updating creator for %s" % model_path(doc)
        doc.creator = new_name
        index.reindex_doc(docid, doc)

    index = catalog['modified_by']
    count, docids, resolver = search(modified_by=old_name)
    for docid in docids:
        doc = resolver(docid)
        if out is not None:
            print >>out, "Updating modified_by for %s" % model_path(doc)
        doc.modified_by = new_name
        index.reindex_doc(docid, doc)
