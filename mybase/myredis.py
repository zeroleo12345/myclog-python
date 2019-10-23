#!/usr/bin/python
#coding:utf-8
""" Reference:
        http://redis-py.readthedocs.io/en/latest/index.html

ERROR:
>>> dir(redis.exceptions)
['AuthenticationError', 'BusyLoadingError', 'ConnectionError', 'DataError', 'ExecAbortError', 'InvalidResponse', 'LockError', 'NoScriptError', 'PubSubError', 'ReadOnlyError', 'RedisError', 'ResponseError', 'TimeoutError', 'WatchError', '__builtins__', '__doc__', '__file__', '__name__', '__package__', 'unicode']
"""

from mybase.mysingleton import Singleton
try:
    import redis
except ImportError as e:
    print """
    need module: redis. Please excute: pip install redis; pip install redis
    HiredisParser is better than PythonParser. OPTIONAL: pip install hiredis
    """
    raise e

class HashEverytime(redis.StrictRedis):
    """ 每次都直接操作数据库, 不缓存数据 """
    def __init__(self, conn_pool):
        super(self.__class__, self).__init__(connection_pool=conn_pool)

    def rpop_n(self, key, n=1):
        """ return: None if the queue is empty """
        if n <= 1: return [self.rpop(key)]
        with self.pipeline() as pipe:
            for i in xrange(n):
                pipe.rpop(key)
            return pipe.execute() # rows = pipe.execute(); filter(lambda x:x, rows)
    def lpop_n(self, key, n=1):
        """ return: None if the queue is empty """
        if n <= 1: return [self.lpop(key)]
        with self.pipeline() as pipe:
            for i in xrange(n):
                pipe.lpop(key)
            return pipe.execute() # rows = pipe.execute(); filter(lambda x:x, rows)

""" 不使用的!只用来查看API参数 """
class __HashEverytime(object):
    def __init__(self, conn_pool):
        self.conn_pool = conn_pool
        self.r = redis.StrictRedis(connection_pool=self.conn_pool)

    def ping(self):
        """ return: 
                True: Success,
                None: Fail.
        """
        return self.r.ping()

    # TYPE: string
    def set(self, key, value):
        """ return: True """
        self.r.set(key, value)
    def get(self, key):
        """ return: str or None """
        return self.r.get(key)

    # TYPE: hash
    def hset(self, key, subkey, value):
        """ return:
                1L when insert new and success,
                0L with no_insert and update success.
        """
        self.r.hset(key, subkey, value)
    def hmset(self, key, _dict):
        """ params:
                _dict: It is **kargs in Inner redis-py!
        return:
                True when success,
                None when failed.
        """
        self.r.hmset(key, _dict)
    def hget(self, key, subkey):
        """ return: 
                str if found and key's type is string,
                dict if found and key's type is hash,
                list if found and key's type is list,
        """
        return self.r.hget(key, subkey)
    def hgetall(self, key):
        """ return:
                dict if found and key's type must be hash
                {} if not found.
            raise:
                redis.exceptions.ResponseError
        """
        return self.r.hgetall(key)
    def hdel(self, key, subkey):
        """ return: the number of element deleted """
        return self.r.hdel(key, subkey)

    # TYPE: Set
    def sadd(self, name, *values):
        """ usage:
                sadd('set', 'member1', 'member2')
            return:
                len of set, when success
        """
        pass
    def smembers(self, name):
        """ return:
                set of members, when success. like: set(['member1', 'member2'])
        """
        pass

    # TYPE: SortSet
    def zadd(name, *args, **kwargs):
        """ params:
                use as:
                    zadd('sortset_key', 1.1, 'name', 2.2, 'name2', name3=3.3, name4=4.4)
                    zadd(key, **_dict)
            return:
                len of sortset, when success
        """
        pass
    def zrem(name, *values):
        """ params:
                use as:
                    _list = ['key1', 'key2']
                    zrem(key, *_list)
            return:
                len of success removed member.
        """
        pass
    def zrange(self, name, start, end, desc=False, withscores=False, score_cast_func=None):
        """ params:
                score_cast_func: default is translate to float
                use as: zrange('key', 0, -1, withscores=False)
            return:
                list. 没有数据返回空列表
        """
        pass

    # TYPE: list
    def lrange(self, key, start, stop): 
        """ human sequence of redis-cli lrange rows, should use rpush.(which push at the tail) """
        return self.r.lrange(key, start, stop)
    def rpush(self, key, value): 
        """ function: push at the tail
            return:
                len of list, when success
        """
        return self.r.rpush(key, value)
    def rpop_n(self, key, n=1):
        """ return: None if the queue is empty """
        if n <= 1: return [self.r.rpop(key)]
        with self.r.pipeline() as pipe:
            for i in xrange(n):
                pipe.rpop(key)
            return pipe.execute() # rows = pipe.execute(); filter(lambda x:x, rows)
    def brpop(self, key, value):
        """ block to rpop """
        return self.r.brpop(key, value)
    def lpush(self, key, value):
        """ push at the top """
        return self.r.lpush(key, value)
    def lpop_n(self, key, n=1):
        """ return: None if the queue is empty """
        if n <= 1: return [self.r.lpop(key)]
        with self.r.pipeline() as pipe:
            for i in xrange(n):
                pipe.lpop(key)
            return pipe.execute() # rows = pipe.execute(); filter(lambda x:x, rows)
    def blpop(self, keys, timeout=0):
        """ func: block to lpop
            params:
                keys: list of key
                timeout: seconds. bloking until recv when it is 0; 不阻塞请使用命令: lpop
            return:
                tuple of (key, value)
        """
        return self.r.blpop(keys, timeout)
    def llen(self, key):
        """ return: count of the list """
        return self.r.llen(key)
    def hlen(self, key):
        """ return: count of the hash """
        return self.r.hlen(key)

    # TYPE: all
    def delete(self, key):
        """ return: the number of element deleted """
        return self.r.delete(key)

    def evalsha(self, sha, numkeys, *keys_and_args):
        return self.r.evalsha(sha, numkeys, *keys_and_args)

class HashCache(dict):
    __metaclass__ = Singleton # 单例
    """ 缓存不经常变动的数据. """
    def __init__(self, conn_pool):
        self.conn_pool = conn_pool
        self.r = redis.StrictRedis(connection_pool=self.conn_pool)
    def ping(self):
        """ return: 
                True: Success,
                None: Fail.
        """
        return self.r.ping()

    # string
    def set(self, key, value):
        return self.r.set(key, value)
    def get(self, key):
        """ return: string or None """
        if not self.has_key(key): self[key] = self.r.get(key)
        return self[key]

    # hash
    def hset(self, key, subkey, value):
        self.r.hset(key, subkey, value)
    def hget(self, key, subkey):
        """ return: dict """
        return self.r.hget(key, subkey)
    def hmset(self, key, _dict):
        self.r.hmset(key, _dict)
    def hgetall(self, key):
        """ return: dict """
        return self.r.hgetall(key)
    def hdel(self, key, subkey):
        """ return: the number of element deleted """
        return self.r.hdel(key, subkey)

    def delete(self, key):
        """ return: the number of element deleted """
        return self.r.delete(key)

    def reload(self):
        """ 定时重读数据 """
        if self.r.ping():
            self.clear()
            self.load()
            return True
        else:
            return False

    def load(self):
        """ 读取数据 """
        keys = self.r.keys('%s*'%self.prefix)
        l = len(self.prefix)
        for k in keys:
            #print k
            self[k[l:]] = self.r.hgetall(k)

    def save(self):
        r = self.r
        for k in self.keys():
            r.hmset(self.prefix+k, self[k])

    def clear_db(self):
        """ Clear all items with the prefix from redis """
        self.clear()
        ks = self.r.keys('%s*'%self.prefix)
        if len(ks) > 0:
            self.r.delete(*ks)

    def save_from_dict(self, dd):
        """ Do a clear_db, then save the dict passed in to redis
        paramter:
            dd: the dictionary to be set to the redis and the buffer
        """
        self.clear()
        self.update(dd)
        self.save()

class MyRedisConnPoolManager():
    #__metaclass__ = Singleton # 这里不能使用单例, 因为有链接多个db的需求!
    def __init__(self, host='127.0.0.1', port=6379, password='', db=0, socket_timeout=None, socket_connect_timeout=2):
        """ params:
                socket_timeout: specific timeout(seconds) for reading; None for blocking.
                socket_connect_timeout: specific timeout(seconds) for connect; None for blocking.
        """
        self.conn_pool = redis.BlockingConnectionPool(host = host, port = port, password = password, db = db,
                socket_timeout = socket_timeout, socket_connect_timeout = socket_connect_timeout)

if __name__=="__main__":
    # from mybase.myredis import MyRedisConnPoolManager, HashEverytime
    _poolmgr = MyRedisConnPoolManager( host = 'zeroleo1234.chickenkiller.com', port = 6666, password = 'xiaobaizhushou', db = 1)
    ## ./redis-cli.exe -h 127.0.0.1 -p 6379 -a '' -n 1

    def test_HashEverytime_rpush():
        g_hash_everytime = HashEverytime(_poolmgr.conn_pool)
        ret = g_hash_everytime.rpush('LIST1', '1')
        print "rpush.ret:", ret
        ret = g_hash_everytime.rpush('LIST2', '2')
        print "rpush.ret:", ret
    def test_HashEverytime_blpop():
        g_hash_everytime = HashEverytime(_poolmgr.conn_pool)
        ret = g_hash_everytime.blpop(['LIST1', 'LIST2'], timeout=0)
        print "blpop.ret:", ret
    def test_HashEverytime_evalsha():
        g_hash_everytime = HashEverytime(_poolmgr.conn_pool)
        keys_and_args = ["Signin_1234567890@chatroom_zeroleo12345", "2017-02-20", "2017-02-19"]
        ret = g_hash_everytime.evalsha('511b86a8f8e8e3677783f9efce342528a8ff27bb', 1, *keys_and_args)
        print "evalsha.ret:", ret

    def test_HashEverytime_hset_hgetall():
        g_hash_everytime = HashEverytime(_poolmgr.conn_pool)
        key = 'TestHash'
        subkey = 'key'
        value = 'value'
        ret = g_hash_everytime.hset(key, subkey, value)
        print "hset.ret:", ret
        rows = g_hash_everytime.hgetall(key)
        print "hgetall.rows:", rows
    def test_HashEverytime_hmset_hgetall():
        g_hash_everytime = HashEverytime(_poolmgr.conn_pool)
        key = 'TestHash'
        _dict = {'key1':'value1', 'key2':'value2'}
        ret = g_hash_everytime.hmset(key, _dict)
        print "hmset.ret:", ret
        rows = g_hash_everytime.hgetall(key)
        print "hgetall.rows:", rows
    def test_HashEverytime_zadd_zrange():
        g_hash_everytime = HashEverytime(_poolmgr.conn_pool)
        key = 'TestSortSet'
        _dict = {'key1':'1', 'key2':'2'}
        ret = g_hash_everytime.zadd(key, **_dict)
        print "zadd.ret:", ret
        rows = g_hash_everytime.zrange(key, 0, -1, withscores=False)
        print "zrange withscores=False.rows:", rows
        rows = g_hash_everytime.zrange(key, 0, -1, withscores=True)
        print "zrange withscores=True.rows:", rows
        print "translate to dict:", dict(rows)
        #print [k for k,v in dict(rows).items() if v>=2]
        _list = ['key1', 'key2']
        rows = g_hash_everytime.zrem(key, *_list)
        print "zrem.rows:", rows
    def test_HashEverytime_sadd_smembers():
        g_hash_everytime = HashEverytime(_poolmgr.conn_pool)
        key = 'TestSet'
        ret = g_hash_everytime.sadd(key, 'member1', 'member2')
        print "smembers.ret:", ret
        ret = g_hash_everytime.smembers(key)
        print "smembers.ret:", ret

    def test_HashCache_set_get():
        g_hash_cache = HashCache(_poolmgr.conn_pool)
        key = sys.argv[1]
        value = sys.argv[2]
        ret = g_hash_cache.set(key, value)
        print "set.ret:", ret
        rows = g_hash_cache.get(key)  # get: Str
        print "get.rows:", rows

if __name__=="__main__":
    def Usage():
        print u"""
        python ./{0} test_HashCache_set_get "hashcache_table" "value"
        python ./{0} test_HashEverytime_hset_hgetall
        python ./{0} test_HashEverytime_blpop; python ./{0} test_HashEverytime_rpush;
        """.format(__file__)
    import sys
    if len(sys.argv) == 1: Usage(), sys.exit()
    function = sys.argv[1]
    del sys.argv[1]
    eval(function)()
