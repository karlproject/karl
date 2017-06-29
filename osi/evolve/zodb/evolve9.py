
def evolve(root):
    try:
        del root.last_gsa_sync
    except AttributeError:
        pass
