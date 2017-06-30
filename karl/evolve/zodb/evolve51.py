from karl.models.profile import CaseInsensitiveOOBTree

def evolve(site):
    site['profiles'].ssoid_to_name = CaseInsensitiveOOBTree()
