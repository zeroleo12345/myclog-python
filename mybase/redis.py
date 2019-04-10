# 第三方库
import redis
#
from settings import REDIS_URI


class Redis(redis.StrictRedis):
    caches = {}

    def __init__(self):
        connection_pool = redis.BlockingConnectionPool.from_url(REDIS_URI)
        super(self.__class__, self).__init__(connection_pool=connection_pool)


redis_client = Redis()

