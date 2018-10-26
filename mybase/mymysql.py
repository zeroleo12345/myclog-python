#!/usr/bin/python
#coding:utf-8
""" Reference:
    https://pypi.python.org/pypi/MySQL-python/1.2.5
    https://sourceforge.net/projects/mysql-python/files/mysql-python/1.2.3/
"""
try:
    import MySQLdb
    import MySQLdb.cursors # 设置结果集用字典返回
except ImportError as e:
    print """ 
    need module: MySQL-python. Please excute: pip install MySQL-python
    """
    raise e
from mybase.mysingleton import Singleton

"""
MySQLdb异常:
Warning 当有严重警告时触发，例如插入数据是被截断等等。必须是 StandardError 的子类。
Error   警告以外所有其他错误类。必须是 StandardError 的子类。
InterfaceError  当有数据库接口模块本身的错误（而不是数据库的错误）发生时触发。 必须是Error的子类。
DatabaseError   和数据库有关的错误发生时触发。 必须是Error的子类。
DataError   当有数据处理时的错误发生时触发，例如：除零错误，数据超范围等等。 必须是DatabaseError的子类。
OperationalError    指非用户控制的，而是操作数据库时发生的错误。例如：连接意外断开、 数据库名未找到、事务处理失败、内存分配错误等等操作数据库是发生的错误。 必须是DatabaseError的子类。
IntegrityError  完整性相关的错误，例如外键检查失败等。必须是DatabaseError子类。
InternalError    数据库的内部错误，例如游标（cursor）失效了、事务同步失败等等。 必须是DatabaseError子类。
ProgrammingError    程序错误，例如数据表（table）没找到或已存在、SQL语句语法错误、 参数数量错误等等。必须是DatabaseError的子类。
NotSupportedError   不支持错误，指使用了数据库不支持的函数或API等。例如在连接对象上 使用.rollback()函数，然而数据库并不支持事务或者事务已关闭。 必须是DatabaseError的子类。
"""

"""
Mysql数据类型:
    TIMESTAMP:  bytes: 4     range: 19700101080001——20380119111407
    第一，可以使用CURRENT_TIMESTAMP;
    第二，输入NULL，系统自动输入当前的TIMESTAMP;
    第三，无任何输入，系统自动输入当前的TIMESTAMP;
    另外有很特殊的一点：TIMESTAMP的数值是与时区相关
"""
class MysqlBase(dict):
    def __init__( self, conn ):
        self.conn = conn

    def create( self, sql ):
        cur = self.conn.cursor()
        try:
            return cur.execute( sql )
        except Exception as e:
            raise e
        finally:
            cur.close()

    def select( self, sql, data_tuple=() ):
        """ return: rows dict """
        cur = self.conn.cursor()
        try:
            if data_tuple:
                ret = cur.execute( sql, data_tuple )
            else:
                ret = cur.execute( sql )
            return cur.fetchall()
        except Exception as e:
            raise e
        finally:
            cur.close()

    def insert( self, sql, data_tuple ):
        cur = self.conn.cursor()
        try:
            ret = cur.execute( sql, data_tuple )
            if ret: self.conn.commit()
            return ret
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cur.close()

    def update( self, sql, data_tuple ):
        cur = self.conn.cursor()
        try:
            ret = cur.execute( sql, data_tuple )
            if ret: self.conn.commit()
            return ret
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cur.close()

DictCursor = MySQLdb.cursors.DictCursor
class MyMysqlConnPoolManager:
    __metaclass__ = Singleton # 单例
    def __init__(self, host, port, user, passwd, db, charset='utf8', cursorclass=DictCursor):
        """ cursorclass: 设置结果集用什么类型返回 """
        self.conn = MySQLdb.connect( host = host, port = port, user = user, passwd = passwd, db = db, charset = charset, cursorclass = cursorclass )
    def __del__(self):
        self.conn.close()

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
            if ret: cur.scroll(0,'absolute') # 用于游标定位到第一条数据
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
    """ HOW TO USE Singleton: """
    from mymysql import MyMysqlConnPoolManager, DictCursor, MysqlBase
    _poolmgr = MyMysqlConnPoolManager(
        host = '127.0.0.1',
        port = 3306,
        user = 'root',
        passwd = 'root666',
        db = 'guanjia',
        charset = 'utf8', # utf8mb4
        cursorclass = DictCursor, # 设置结果集用字典返回
    )  

    # mysql -uroot -proot666 -h127.0.0.1 -P3306
    def test_class():
        db = MysqlBase(_poolmgr.conn)
        rows = db.select('SELECT * from performance_schema.users')
        print rows

    def test_raw():
        #test_create(_poolmgr.conn)
        #test_insert(_poolmgr.conn)
        #test_multi_insert(_poolmgr.conn)
        #test_select_one(_poolmgr.conn)
        #test_select_prepare(_poolmgr.conn)
        #test_update(_poolmgr.conn)
        #test_select_one(_poolmgr.conn)
        #test_delete(_poolmgr.conn)
        _poolmgr.conn.commit()

if __name__ == "__main__":
    def Usage():
        print u"""
        python ./{0} test_class
        python ./{0} test_raw
        """.format(__file__)
    import sys 
    if len(sys.argv) == 1: Usage(), sys.exit()
    function = sys.argv[1]
    del sys.argv[1]
    eval(function)()
