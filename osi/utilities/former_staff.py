from zope.component import getUtility

from pyramid.renderers import render
from pyramid.traversal import model_path
from repoze.sendmail.interfaces import IMailDelivery

from repoze.postoffice.message import Message
from karl.utils import find_communities
from karl.utils import find_users
from karl.utils import get_setting

def make_non_staff(profile, inform_moderators=True):
    """
    When a user is removed from the KarlStaff role, their community
    memberships are removed. Moderators of their communities are optionally
    informed via email.
    """
    id = profile.__name__
    moderators = {}
    users = find_users(profile)
    profile.categories = {}
    for group in list(users.get_by_id(id)['groups']):
        if group.startswith('group.community'):
            # Remove user from group
            users.remove_user_from_group(id, group)
            if not inform_moderators:
                continue

            # Keep track of moderators we need to email making sure
            # each moderator is emailed only once and each community is
            # only mentioned once in any given email.
            community_name = group.split(':')[1]
            moderators_group = ('group.community:%s:moderators' %
                                community_name)
            for moderator in users.users_in_group(moderators_group):
                if moderator == id:
                    continue # Really should only come up in unittests
                if moderator not in moderators:
                    moderators[moderator] = set()
                moderators[moderator].add(community_name)

    if not inform_moderators:
        return

    communities = find_communities(profile)
    profiles = profile.__parent__
    mailer = getUtility(IMailDelivery)
    for moderator_id in moderators:
        moderator = profiles[moderator_id]
        msg = Message()
        msg['From'] = get_setting(profile, 'admin_email')
        msg['To'] = '%s <%s>' % (moderator.title, moderator.email)
        msg['Subject'] = 'Notice that %s is now former staff' % profile.title
        former_communities = sorted(
            [communities[c] for c in moderators[moderator_id]],
            key=lambda x:x.title
        )
        app_url = get_setting(profile, 'offline_app_url')
        communities_info = [
            dict(title=c.title, unremove_url='%s%s?user_id=%s' %
                 (app_url, model_path(c, 'members', 'add_existing.html'), id))
            for c in former_communities
        ]
        body = render(
            'templates/email_notify_former_staff.pt',
            dict(name=profile.title,
                 communities=communities_info),
        )
        if isinstance(body, unicode):
            body = body.encode('UTF-8')
        msg.set_payload(body, 'UTF-8')
        msg.set_type('text/html')

        mailer.send([msg['To']], msg)


