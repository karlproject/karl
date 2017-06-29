from karl.utilities.rename_user import rename_user
import sys

def evolve(root):
    try:
        rename_user(root, 'jonathanhulland', 'jhulland', True, sys.stdout)
    except ValueError:
        pass
