import redis

from pyramid.traversal import resource_path


class RedisArchiveQueue(object):
    """
    Provides an API for interacting with the work queue for archiving
    communities to Box.  The work queue is stored in Redis.
    """
    COPY_QUEUE_KEY = 'arc2box.copy'

    @classmethod
    def from_settings(cls, settings, prefix='redislog.'):
        prefixlen = len(prefix)
        filtered_by_prefix = (
            (name[prefixlen:], value)
            for name, value in settings.items()
            if name.startswith(prefix))
        settings = {name: value for name, value in filtered_by_prefix
                    if name in ('host', 'port', 'db', 'password')}
        return cls(**settings)

    def __init__(self, host='localhost', port=6379, db=0, password=None):
        self.redis = redis.StrictRedis(
            host=host, port=port, db=db, password=password)

    def queue_for_copy(self, community):
        """
        Adds community to queue for copying.
        """
        self.redis.rpush(self.COPY_QUEUE_KEY, resource_path(community))

    def get_work(self):
        """
        Get the next thing to do.  Block until there is something to do.
        """
        return self.redis.blpop((self.COPY_QUEUE_KEY,))
