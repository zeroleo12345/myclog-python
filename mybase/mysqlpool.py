#!/usr/bin/python
#coding:utf-8
""" Reference:
    MySQL-python: (就是MySQLdb模块)
        https://pypi.python.org/pypi/MySQL-python/1.2.5
        https://sourceforge.net/projects/mysql-python/files/mysql-python/1.2.3/
    MySQLdb API:
        http://mysql-python.sourceforge.net/MySQLdb-1.2.2/
"""
try:
    import MySQLdb
    import MySQLdb.cursors # 设置结果集用字典返回
except ImportError as e:
    print """ 
    Please excute: pip install MySQL-python
    """
    raise e
try:
    from DBUtils.PooledDB import PooledDB
except ImportError as e:
    print """ 
    Please excute: pip install DBUtils
    """
    raise e

IntegrityError = MySQLdb.IntegrityError # 整性相关的错误，例如外键检查失败等。必须是DatabaseError子类
"""
异常:
MySQLdb.Warning 当有严重警告时触发，例如插入数据是被截断等等。必须是 StandardError 的子类。
MySQLdb.Error   警告以外所有其他错误类。必须是 StandardError 的子类。
MySQLdb.InterfaceError  当有数据库接口模块本身的错误（而不是数据库的错误）发生时触发。 必须是Error的子类。
MySQLdb.DatabaseError   和数据库有关的错误发生时触发。 必须是Error的子类。
MySQLdb.DataError   当有数据处理时的错误发生时触发，例如：除零错误，数据超范围等等。 必须是DatabaseError的子类。
MySQLdb.OperationalError    指非用户控制的，而是操作数据库时发生的错误。例如：连接意外断开、 数据库名未找到、事务处理失败、内存分配错误等等操作数据库是发生的错误。 必须是DatabaseError的子类。
MySQLdb.InternalError    数据库的内部错误，例如游标（cursor）失效了、事务同步失败等等。 必须是DatabaseError子类。
MySQLdb.ProgrammingError    程序错误，例如数据表（table）没找到或已存在、SQL语句语法错误、 参数数量错误等等。必须是DatabaseError的子类。
MySQLdb.NotSupportedError   不支持错误，指使用了数据库不支持的函数或API等。例如在连接对象上 使用.rollback()函数，然而数据库并不支持事务或者事务已关闭。 必须是DatabaseError的子类。
"""

"""
Mysql数据类型:
    TIMESTAMP:  bytes: 4     range: 19700101080001——20380119111407
    第一，可以使用CURRENT_TIMESTAMP;
    第二，输入NULL，系统自动输入当前的TIMESTAMP;
    第三，无任何输入，系统自动输入当前的TIMESTAMP;
    另外有很特殊的一点：TIMESTAMP的数值是与时区相关
"""
DictCursor = MySQLdb.cursors.DictCursor
class MysqlPool(object):
    __config = None
    __pool = None
    def __init__(self, config={}):
        # mysql -uroot -proot666 -h127.0.0.1 -P3306
        if not self.__config:
            self.__config = {
                'host': '127.0.0.1',
                'port': 3306,
                'user': 'root',
                'password': '',
                'db': 'guanjia', # 使用指定数据库
                'use_unicode': True,
                'charset': 'utf8', # 数据库连接编码, utf8, utf8mb4
                'mincached': 1, # 启动时连接池中创建的的连接数.(缺省值0: 代表开始时不创建连接)
                'maxcached': 20, # 连接池中允许的闲置的最多连接数量.(缺省值0: 代表不闲置)
                'maxshared': 0, # 最大共享连接数(默认0: 代表都是专用的)如果达到最大数量, 被请求为共享的连接将会被共享使用)
                'maxconnections': 50, # 创建连接池的最大数量(默认0: 代表不限制)
                'maxusage': 0, # 单个连接的最大允许复用次数(缺省值0或False:代表不限制的复用).当达到最大数时,连接会自动重新连接(关闭和重新打开)
                'blocking': False, # 设置连接数到最大时的行为(默认0或False: 代表返回一个错误<toMany......>; 其他代表阻塞直到连接数减少,连接被分配)
                'setsession': None, # 一个可选的SQL命令列表用于准备每个会话，如["set datestyle to german", ...]
            }
            self.__config.update(config)

    def __enter__(self):
        self.conn = self.__get_connection()
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, type, value, trace):
        self.cursor.close()
        self.conn.close()

    def __get_connection(self):
        if not self.__pool:
            if self.__config.has_key('unix_socket') and self.__config['unix_socket']:
                # print 'new mysql connection, unix socket'
                self.__pool = PooledDB(
                        creator=MySQLdb, 
                        unix_socket='/tmp/mysql.sock',
                        # host=self.__config['host'], port=self.__config['port'],
                        user=self.__config['user'],
                        passwd=self.__config['password'],
                        db=self.__config['db'],
                        cursorclass=DictCursor, # 设置结果集用字典返回
                        use_unicode=self.__config['use_unicode'],
                        charset=self.__config['charset'],
                        mincached=self.__config['mincached'],
                        maxcached=self.__config['maxcached'],
                        maxshared=self.__config['maxshared'],
                        maxconnections=self.__config['maxconnections'],
                        maxusage=self.__config['maxusage'],
                        blocking=self.__config['blocking'],
                        setsession=self.__config['setsession']
                    )
            else:
                # print 'new mysql connection, socket'
                self.__pool = PooledDB(
                        creator=MySQLdb, 
                        # unix_socket='/tmp/mysql.sock',
                        host=self.__config['host'], port=self.__config['port'],
                        user=self.__config['user'],
                        passwd=self.__config['password'],
                        db=self.__config['db'],
                        cursorclass=DictCursor, # 设置结果集用字典返回
                        use_unicode=self.__config['use_unicode'],
                        charset=self.__config['charset'],
                        mincached=self.__config['mincached'],
                        maxcached=self.__config['maxcached'],
                        maxshared=self.__config['maxshared'],
                        maxconnections=self.__config['maxconnections'],
                        maxusage=self.__config['maxusage'],
                        blocking=self.__config['blocking'],
                        setsession=self.__config['setsession']
                    )
        return self.__pool.connection()

    def select( self, sql, data_tuple=() ):
        """ return: rows dict """
        self.execute( sql, data_tuple )
        return self.cursor.fetchall()

    def commit( self ):
        return self.conn.commit()
    def rollback( self ):
        return self.conn.rollback()

    def execute( self, sql, data_tuple ):
        if not data_tuple:
            return self.cursor.execute( sql )
        else:
            return self.cursor.execute( sql, data_tuple )

    def insert( self, sql, data_tuple ):
        ret = self.execute( sql, data_tuple )
        if ret: self.commit()
        return ret

    def update( self, sql, data_tuple ):
        ret = self.execute( sql, data_tuple )
        if ret: self.commit()
        return ret

if __name__ == "__main__":
    def test_create(conn):
        print '创建数据表'
        cur = conn.cursor()
        try:
            create_sql = ''' create table IF NOT EXISTS student(
                        id int,
                        name varchar(20),
                        class varchar(30),
                        age varchar(10))
                        '''
            ret = cur.execute( create_sql )
        except Exception as e:
            raise e
        finally:
            cur.close()
        print 'ret:', ret

    def test_insert(conn):
        print '插入一条数据'
        cur = conn.cursor()
        try:
            ret = cur.execute("insert into student values('2','Tom','3 year 2 class','9')")
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
        print 'ret:', ret

    def testPrepare_insert(conn):
        print '插入Prepare数据'
        cur = conn.cursor()
        sqli= 'insert into student values(%s,%s,%s,%s)'
        try:
            ret = cur.execute( sqli, ('3','Huhu','2 year 1 class','7') )
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
        print 'ret:', ret

    def test_multi_insert(conn):
        print '插入多条数据'
        cur = conn.cursor()
        sqli="insert into student values(%s,%s,%s,%s)"
        try:
            ret = cur.executemany(sqli, [
                ('3','Tom','1 year 1 class','6'),
                ('3','Jack','2 year 1 class','7'),
                ('3','Yaheng','2 year 2 class','7'),
                ])
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
        print 'ret:', ret

    def test_select_prepare( conn, data_tuple=(2,3,) ):
        '''
        '''
        print 'select Prepare数据表 '
        cur = conn.cursor()
        try:
            ret = cur.execute("select id, name, class, age from student where id in (%s,%s)", data_tuple )
            print '表中有%d条数据' % ret
            for i in range(0, ret):
                row = cur.fetchone()
                print 'row:', row
            if ret: cur.scroll(0,'absolute') # 用于游标定位到第一条数据
        except Exception as e:
            raise e
        finally:
            cur.close()

    def test_select_one(conn):
        '''
            row: (3L, 'Tom', '1 year 1 class', '6')
            row: (3L, 'Jack', '2 year 1 class', '7')
            row: (3L, 'Yaheng', '2 year 2 class', '7')
        '''
        print 'select数据表 fetchone'
        cur = conn.cursor()
        try:
            ret = cur.execute("select id, name, class, age from student")
            print '表中有%d条数据' % ret
            for i in range(0, ret):
                row = cur.fetchone()
                print 'row:', row
            if ret: cur.scroll(0,'absolute') # 用于游标定位到第一条数据
        except Exception as e:
            raise e
        finally:
            cur.close()

    def test_select_multi(conn):
        '''
            row: (3L, 'Tom', '1 year 1 class', '6')
            row: (3L, 'Jack', '2 year 1 class', '7')
            row: (3L, 'Yaheng', '2 year 2 class', '7')
        '''
        print 'select数据表 fetchmany'
        cur = conn.cursor()
        try:
            ret = cur.execute("select id, name, class, age from student")
            print '表中有%d条数据' % ret
            rows = cur.fetchmany( ret )
            for row in rows:
                print row
            if ret: cur.scroll(0,'absolute') # 用于游标定位到第一条数据
        except Exception as e:
            raise e
        finally:
            cur.close()

    def testSelectAll(conn):
        '''
            rows: ((3L, 'Tom', '1 year 1 class', '6'), (3L, 'Jack', '2 year 1 class', '7'), (3L, 'Yaheng', '2 year 2 class', '7'))
        '''
        print 'select数据表 fetchone'
        cur = conn.cursor()
        try:
            ret = cur.execute("select id, name, class, age from student")
            print '表中有%d条数据' % ret
            rows = cur.fetchall()
            print 'rows:', rows
            if ret: cur.scroll(0, 'absolute') # 用于游标定位到第一条数据
        except Exception as e:
            raise e
        finally:
            cur.close()

    def test_update(conn):
        cur = conn.cursor()
        print '更新数据'
        try:
            ret = cur.execute("update student set class='3 year 1 class' where name = 'Tom'")
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
        print 'ret:', ret

    def test_delete(conn):
        print 'delete数据'
        cur = conn.cursor()
        try:
            ret = cur.execute("delete from student")
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
        print 'ret:', ret

if __name__ == "__main__":
    import traceback

    from mybase.mysqlpool import MysqlPool
    config = {
        'unix_socket': '/tmp/mysql.sock',
        # 'host': '127.0.0.1', 'port': 3333,
        'user': 'root',
        'password': 'password',
        'db': 'guanjia', # 使用指定数据库
        'use_unicode': True,
        'charset': 'utf8mb4', # 数据库连接编码
        'mincached': 1, # 启动时连接池中创建的的连接数.(缺省值0: 代表开始时不创建连接)
        'maxcached': 20, # 连接池中允许的闲置的最多连接数量.(缺省值0: 代表不闲置)
        'maxshared': 0, # 最大共享连接数(默认0: 代表都是专用的)如果达到最大数量, 被请求为共享的连接将会被共享使用)
        'maxconnections': 50, # 创建连接池的最大数量(默认0: 代表不限制)
        'maxusage': 0, # 单个连接的最大允许复用次数(缺省值0或False:代表不限制的复用).当达到最大数时,连接会自动重新连接(关闭和重>新打开)
        'blocking': False, # 设置连接数到最大时的行为(默认0或False: 代表返回一个错误<toMany......>; 其他代表阻塞直到连接数减少,>连接被分配)
        'setsession': None, # 一个可选的SQL命令列表用于准备每个会话，如["set datestyle to german", ...]
    }
    def test_class_select():
        with MysqlPool(config) as p:
            rows = p.select('SELECT * FROM performance_schema.users WHERE USER=%s', ('root',))
            if rows:
                print rows
            else:
                print 'not exists row'
    def test_class_insert():
        with MysqlPool(config) as p:
            try:
                # 若需插入mysql的null, 参数为None
                ret = p.execute(
                    'INSERT INTO balance(openid, btype, money) VALUES(%s, %s, %s)',
                    ('test', 9999, 10)
                )
                p.commit()
                print ret
            except IntegrityError:
                log.w('insert fail, IntegrityError')
            except:
                p.rollback()
                print traceback.format_exc()
    def test_class_insert_utf8mb4():
        with MysqlPool(config) as p:
            try:
                content = "@\xe7\x88\xb1\xe5\xbf\x83\xe5\xb0\x8f\xe6\xa9\x99\xe5\xad\x90\xf0\x9f\x8d\x8a\xe2\x80\x85[\xe5\xa5\xb8\xe7\xac\x91]"
                print repr( content )
                print content
                unicode_content = content.decode('utf8')
                print repr( unicode_content )
                print unicode_content
                # 若需插入mysql的null, 参数为None. (其中create_time | timestamp)
                ret = p.execute(
                    'INSERT INTO message(type, is_send, status, create_time, content) VALUES(%s, %s, %s, %s, %s)',
                    (1, 0, 1, "2017-10-11 00:00:00", content)
                )
                p.commit()
                print ret
            except:
                p.rollback()
                print traceback.format_exc()
    def test_class_insert_or_update():
        with MysqlPool(config) as p:
            try:
                # 插入记录返回1; 更新记录返回2;
                ret = p.execute(
                    'INSERT INTO balance(openid, btype, money) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE money=money+VALUES(money)',
                    ('123', 9999, 10)
                )
                p.commit()
                print ret
            except:
                p.rollback()
                print traceback.format_exc()
    def test_class_update():
        with MysqlPool(config) as p:
            try:
                # insert into balance(openid, btype, money) VALUES('test', 9999, 10);
                # 有更新返回1; 没有符合记录,或者原记录不变返回0;
                ret = p.execute(
                    'UPDATE balance SET money=money-%s WHERE openid=%s and money>=%s',
                    (10, 'test', 10)
                )
                p.commit()
                print ret
            except:
                p.rollback()
                print traceback.format_exc()

    def test_raw():
        #test_create(_poolmgr.conn)
        #test_insert(_poolmgr.conn)
        #test_multi_insert(_poolmgr.conn)
        #test_select_one(_poolmgr.conn)
        #test_select_prepare(_poolmgr.conn)
        #test_update(_poolmgr.conn)
        #test_select_one(_poolmgr.conn)
        #test_delete(_poolmgr.conn)
        pass

if __name__ == "__main__":
    def Usage():
        print u"""
        python ./{0} test_class_select
        python ./{0} test_class_insert
        python ./{0} test_class_insert_utf8mb4
        python ./{0} test_class_update
        python ./{0} test_class_insert_or_update
        python ./{0} test_raw
        """.format(__file__)
    import sys 
    if len(sys.argv) == 1: Usage(), sys.exit()
    function = sys.argv[1]
    del sys.argv[1]
    eval(function)()
