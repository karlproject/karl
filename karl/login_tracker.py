import logging

import user_agents

from karl.utils import get_setting


logger = logging.getLogger('failed_logins')
var = get_setting(None, 'var')
filehandler = logging.FileHandler('%s/log/failed_logins.log' % var)
filehandler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
filehandler.setFormatter(formatter)
logger.addHandler(filehandler)


def log_failed_login(request, login):
    client_addr = request.remote_addr
    forwarded = request.headers.get('X-Forwarded-For', None)
    if forwarded is not None:
        client_addr = forwarded.split(',')[0].strip()
    user_agent = 'Unknown browser'
    if request.user_agent is not None:
        user_agent = user_agents.parse(request.user_agent)
    user_agent = request.user_agent
    message = '%s - %s - %s' % (client_addr,
                                str(user_agent),
                                login)
    logger.info(message)
