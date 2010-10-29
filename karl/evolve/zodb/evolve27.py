"""
Ensure referential integrity between user info and logins.
"""
from karl.utils import find_users
def evolve(root):
    users = find_users(root)
    data = users.data
    logins = users.logins
    for userid, info in list(data.items()):
        login = info['login']
        if login not in logins:
            print "Added %s to logins."
            logins[login] = userid
        elif logins[login] != userid:
            print "Updated login for %s from %s to %s." % (
                userid, info['login'], userid)
            info['login'] = userid
            data[userid] = info  # trigger persistence

    for login, userid in list(logins.items()):
        if userid not in data or data[userid]['login'] != login:
            print "Removing %s from logins." % login
            del logins[login]
