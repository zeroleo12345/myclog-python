#!/usr/bin/python
#coding:utf-8
""" Reference:
        http://redis-py.readthedocs.io/en/latest/index.html

ERROR:
>>> dir(redis.exceptions)
['AuthenticationError', 'BusyLoadingError', 'ConnectionError', 'DataError', 'ExecAbortError', 'InvalidResponse', 'LockError', 'NoScriptError', 'PubSubError', 'ReadOnlyError', 'RedisError', 'ResponseError', 'TimeoutError', 'WatchError', '__builtins__', '__doc__', '__file__', '__name__', '__package__', 'unicode']
"""

try:
    import redis
except ImportError as e:
    print """ MISS module!
    Please excute: pip install redis
    HiredisParser is better than PythonParser. OPTIONAL: pip install hiredis
    """
    raise e

class HashEverytimePool(redis.StrictRedis):
    """ 每次都直接操作数据库, 不缓存数据 """
    __pool = {}
    __config = {}
    def __init__(self, config={}):
        # ./redis-cli.exe -h 127.0.0.1 -p 6379 -a '' -n 1
        db = int( config['db'] )
        if not self.__config.has_key( db ):
            self.__config[db] = {
                #'path': '/tmp/redis.sock', # 若选用unix domain socket, 请关闭注释
                'host': '127.0.0.1', 'port': 6666,
                'password': 'xiaobaizhushou',
                'db': 1, # 使用第几个库
                'socket_timeout': None, # specific timeout(seconds) for reading; None for blocking.
                'socket_connect_timeout': 2, # specific timeout(seconds) for connect; None for blocking.
            }
            self.__config[db].update(config)
        if not self.__pool.has_key( db ):
            if self.__config[db].has_key('path') and self.__config[db]['path']:
                # print 'new redis Connection[{}], unix socket:{}'.format(db, self.__config[db]['path'])
                self.__pool = redis.BlockingConnectionPool(
                        connection_class = redis.UnixDomainSocketConnection,
                        path = self.__config[db]['path'],
                        password = self.__config[db]['password'],
                        db = self.__config[db]['db'],
                        socket_timeout = self.__config[db]['socket_timeout'],
                )
            else:
                # print 'new redis Connection[{}], socket. host:{}, port:{}'.format(db, self.__config[db]['host'], self.__config[db]['port'])
                self.__pool = redis.BlockingConnectionPool(
                        connection_class = redis.Connection,
                        host = self.__config[db]['host'],
                        port = self.__config[db]['port'],
                        password = self.__config[db]['password'],
                        db = self.__config[db]['db'],
                        socket_timeout = self.__config[db]['socket_timeout'],
                        socket_connect_timeout = self.__config[db]['socket_connect_timeout'],
                )
        super(self.__class__, self).__init__(connection_pool=self.__pool)

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
    def __init__(self, pool):
        self.__pool = pool
        self.r = redis.StrictRedis(connection_pool=self.__pool)

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
                    方式1: _list = ['key1', 'key2']; zrem(key, *_list)
                    方式2: zrem(key, 'key1', 'key2', 'key3')
            return:
                len of success removed member.
        """
        pass
    def zrange(self, name, start, end, desc=False, withscores=False, score_cast_func=None):
        """ params:
                score_cast_func: default is translate to float
                use as: zrange('key', 0, -1, withscores=False)
            return:
                list, when success
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


if __name__=="__main__":
    from mybase.redispool import HashEverytimePool
    import platform

    config = {
        'path': '/tmp/redis.sock', # 若选用unix domain socket, 请关闭注释
        'host': '127.0.0.1', 'port': 6666,
        'password': 'xiaobaizhushou',
        'db': 1, # 使用第几个库
        'socket_timeout': None, # specific timeout(seconds) for reading; None for blocking.
        'socket_connect_timeou': 2, # specific timeout(seconds) for connect; None for blocking.
    }
    if platform.system() == 'Windows': config.pop('path', None) # Window下不支持使用socket.AF_UNIX
    g_hash_everytime = HashEverytimePool(config)

    def test_HashEverytime_rpush():
        ret = g_hash_everytime.rpush('LIST1', '1')
        print "rpush.ret:", ret
        ret = g_hash_everytime.rpush('LIST2', '2')
        print "rpush.ret:", ret

    def test_HashEverytime_blpop():
        keys = ['LIST1', 'LIST2']
        ret = g_hash_everytime.blpop(keys, timeout=0)
        print "blpop %s, ret:%s" % (keys, ret)

    def test_HashEverytime_evalsha():
        keys_and_args = ["Signin_1234567890@chatroom_zeroleo12345", "2017-02-20", "2017-02-19"]
        ret = g_hash_everytime.evalsha('511b86a8f8e8e3677783f9efce342528a8ff27bb', 1, *keys_and_args)
        print "evalsha.ret:", ret

    def test_HashEverytime_hset_hgetall_hmget_hdel():
        key = 'TestHash'
        subkey = 'subkey'
        value = 'value'
        ret = g_hash_everytime.hset(key, subkey, value)
        print "hset %s %s %s, ret:%s" % (key, subkey, value, ret)
        ret = g_hash_everytime.hgetall(key)
        print "hgetall, ret:", ret
        subkeys = [subkey]
        ret = g_hash_everytime.hmget(key, ['subkey', 'non_exist'])
        print "hmget, ret:", ret
        ret = g_hash_everytime.hdel(key, *subkeys)
        print "hdel, ret:", ret

    def test_HashEverytime_dump_restore():
        key = 'TestDump'
        newkey = 'TestDump2'
        value = g_hash_everytime.dump(key)
        print "dump %s, ret:%s" % (key, value)
        if value:
            ret = g_hash_everytime.restore(newkey, ttl=0, value=value, replace=True)
            print "restore, ret:", ret

    def test_HashEverytime_hmset_hgetall():
        # Hash
        key = 'TestHash'
        _dict = {'key1':'value1', 'key2':'value2'}
        ret = g_hash_everytime.hmset(key, _dict)
        print "hmset.ret:", ret
        rows = g_hash_everytime.hgetall(key)
        print "hgetall.rows:", rows

    def test_HashEverytime_zadd_zrange():
        # SortSet
        import time
        key = 'TestSortSet'
        subkey = "subkey"
        value = 100.0
        _dict = {subkey: value, 'key1': time.time(), 'key2': time.time()+100}
        ret = g_hash_everytime.zadd(key, **_dict)
        print "zadd.ret:", ret
        start = 0
        stop = -1
        withscores=False
        rows = g_hash_everytime.zrange(key, start, stop, withscores=withscores)
        print "zrange, [{}, {}], withscores={}, rows:{}".format( start, stop, withscores, rows )
        start = 0
        stop = -1
        withscores=True
        rows = g_hash_everytime.zrange(key, start, stop, withscores=withscores)
        print "zrange, [{}, {}], withscores={}, rows:{}".format( start, stop, withscores, rows )
        print "translate to dict:", dict(rows)
        #print [k for k,v in dict(rows).items() if v>=2]
        start = '-inf'
        stop = '+inf'
        pos = 0
        cnt = 1
        rows = g_hash_everytime.zrangebyscore(key, start, stop, withscores=False, start=pos, num=cnt)
        print "zrangebyscore, pos:{}, cnt:{}, [{},{}], rows:{}".format( pos, cnt, start, stop, rows )
        start = '-inf'
        stop = '+inf'
        pos = 0
        cnt = 9999
        rows = g_hash_everytime.zrangebyscore(key, start, stop, withscores=False, start=pos, num=cnt)
        print "zrangebyscore, pos:{}, cnt:{}, [{},{}], rows:{}".format( pos, cnt, start, stop, rows )
        start = time.time()
        stop = '+inf'
        pos = 0
        cnt = 1
        rows = g_hash_everytime.zrangebyscore(key, start, stop, withscores=False, start=pos, num=cnt)
        print "zrangebyscore, pos:{}, cnt:{}, [{},{}], rows:{}".format( pos, cnt, start, stop, rows )
        _list = ['key1', 'key2']
        rows = g_hash_everytime.zrem(key, *_list)
        print "zrem.rows:", rows
        ret = g_hash_everytime.zscore(key, subkey)
        print "zscore, ret:{}, type(ret):{}".format( ret, type(ret) )

    def test_HashEverytime_sadd_smembers():
        # Set
        key = 'TestSet'
        ret = g_hash_everytime.sadd(key, 'member1', 'member2')
        print "smembers.ret:", ret
        ret = g_hash_everytime.smembers(key)
        print "smembers.ret:", ret

    def test_HashEverytime_set_get():
        import os, msgpack
        key = "mytest"
        value = os.urandom(10)
        ret = g_hash_everytime.set( key, msgpack.dumps(value) )
        print "set value:%s, ret:%s" % (value, ret)
        ret = g_hash_everytime.get(key)  # get: Str
        print "get.rows:", msgpack.loads(ret)

if __name__=="__main__":
    def Usage():
        print u"""
        python ./{0} test_HashEverytime_hset_hgetall_hmget_hdel
        python ./{0} test_HashEverytime_zadd_zrange
        python ./{0} test_HashEverytime_set_get
        python ./{0} test_HashEverytime_dump_restore
        python ./{0} test_HashEverytime_blpop; python ./{0} test_HashEverytime_rpush;
        """.format(__file__)
    import sys
    if len(sys.argv) == 1: Usage(), sys.exit()
    function = sys.argv[1]
    del sys.argv[1]
    eval(function)()

""" API返回结果参考:
hmget( key, subkey_list )  返回: ['value1', 'value2']
hgetall( key )  返回: {'subkey': 'value'}
zrange( key, 0, -1, withscores=True )  返回: [ ('subkey1', 1), ('subkey2', 2) ]
zrange( key, 0, -1, withscores=False )  返回: ['subkey1', 'subkey2']
g_hash_everytime.zscore('ServiceWorker','wxid_z7x7n174cedb1') 返回: 1.None; 2.score值
"""
