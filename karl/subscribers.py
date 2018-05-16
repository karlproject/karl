import logging

import user_agents

from pyramid.security import authenticated_userid
from pyramid.security import forget

from karl.utils import find_profiles
from karl.utils import get_setting


logger = logging.getLogger('request_logger')
var = get_setting(None, 'var')
if var is not None:
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
        profile = None
        try:
            profiles = find_profiles(request.context)
        except AttributeError:
            profiles = None
        if profiles is not None:
            profile = profiles.get(userid, None)
        if profile is not None and profile.email:
            email = '(%s)' % profile.email
        client_addr = request.remote_addr
        forwarded = request.headers.get('X-Forwarded-For', None)
        if forwarded is not None:
            client_addr = forwarded.split(',')[0].strip()
        user_agent = 'Unknown browser'
        if request.user_agent is not None:
            user_agent = user_agents.parse(request.user_agent)
        message = '%s - %s - %s %s - %s' % (client_addr,
                                            str(user_agent),
                                            userid or 'Anonymous',
                                            email,
                                            request.path)
        if not (request.path.startswith('/login.html') and
                client_addr.startswith('195.62.')):
            logger.info(message)


def session_restriction(event):
    request = event.request
    response = event.response
    userid = authenticated_userid(request),
    profile = None
    if userid is not None:
        userid = userid[0]
    try:
        profiles = find_profiles(request.context)
    except AttributeError:
        profiles = None
    if profiles is not None:
        profile = profiles.get(userid, None)
    if profile is not None:
        active_device = profile.active_device
        device_cookie_name = request.registry.settings.get('device_cookie',
                                                            'CxR61DzG3P0Ae1')
        current_device = request.cookies.get(device_cookie_name, None)
        if (active_device and current_device) and current_device != active_device:
            # there was a new login for the profile, so this user is out of luck
            request.session['logout_reason'] = '@@@one-session-only@@@'
            forget_headers = forget(request)
            response.headers.extend(forget_headers)
