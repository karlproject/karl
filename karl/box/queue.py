import redis


class RedisArchiveQueue(object):
    """
    Provides an API for interacting with the work queue for archiving
    communities to Box.  The work queue is stored in Redis.
    """
    def from_settings(self, settings, prefix='redislog.'):
        prefixlen = len(prefix)
        filtered_by_prefix = (
            (name[prefixlen:], value)
            for name, value in settings.items()
            if name.startswith(prefix))
        settings = {name: value for name, value in filtered_by_prefix
                    if name in ('host', 'port', 'db', 'password')}
        return RedisArchiveQueue(**settings)

    def __init__(self, host='localhost', port=6379, db=0, password=None):
        self.redis = redis.StrictRedis(
            host=host, port=port, db=db, password=password)

    def get_community_status(self, community):
        """
        Gets state for a community.  Returns: 'copying', 'reviewing',
        'removing', 'archived', or None
        """
        return self.redis.get(self._community_key(community))

    def _community_key(self, community):
        return 'arc2box-community-' + str(community.docid)
