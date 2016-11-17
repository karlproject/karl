import logging

from pyramid.security import authenticated_userid
from pyramid.security import forget

from karl.utils import find_profiles
from karl.utils import get_setting


logger = logging.getLogger('request_logger')
var = get_setting(None, 'var')
filehandler = logging.FileHandler('%s/log/tracker.log' % var)
filehandler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
filehandler.setFormatter(formatter)
logger.addHandler(filehandler)


def request_logger(event):
    request = event.request
    if not (request.path.startswith('/static') or
            request.path.startswith('/newest_feed_items.json')):
        userid = authenticated_userid(request),
        if userid is not None:
            userid = userid[0]
        email = ''
        profiles = find_profiles(request.context)
        profile = profiles.get(userid, None)
        if profile is not None and profile.email:
            email = '(%s)' % profile.email
        client_addr = request.remote_addr
        forwarded = request.headers.get('X-Forwarded-For', None)
        if forwarded is not None:
            client_addr = forwarded.split(',')[0].strip()
        message = '%s - %s - %s %s - %s' % (client_addr,
                                            request.user_agent,
                                            userid or 'Anonymous',
                                            email,
                                            request.path)
        if not (request.path.startswith('/login.html') and
                client_addr.startswith('195.62.')):
            logger.info(message)

RESTRICTION_TEXT = """
<p>To protect the security of your account, KARL only allows one active user
session at time. Your account has just been accessed from another browser or
device, so this user session has been terminated. To resume this session,
please log out of KARL on any other browsers or devices.</p>

<p>If you did not login to your KARL account from another device, your account
may have been compromised. To protect the integrity of your account, we recommend
that you immediately <a href="https://karl.soros.org/reset_request.html">change
your password</a>. If you have any questions or concerns contact the KARL support
team at karl@soros.zendesk.com.</p>

<p>-The KARL Team</p>
"""

def session_restriction(event):
    request = event.request
    response = event.response
    userid = authenticated_userid(request),
    if userid is not None:
        userid = userid[0]
    profiles = find_profiles(request.context)
    profile = profiles.get(userid, None)
    if profile is not None:
        active_device = profile.active_device
        device_cookie_name = request.registry.settings.get('device_cookie',
                                                            'CxR61DzG3P0Ae1')
        current_device = request.cookies.get(device_cookie_name, None)
        if (active_device and current_device) and current_device != active_device:
            # there was a new login for the profile, so this user is out of luck
            request.session['logout_reason'] = RESTRICTION_TEXT
            forget_headers = forget(request)
            response.headers.extend(forget_headers)
