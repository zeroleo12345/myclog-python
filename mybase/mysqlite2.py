#!/usr/bin/env python.exe
#coding:utf-8

""" Reference:
        https://docs.python.org/2/library/sqlite3.html
"""

import sqlite3 # 标准库

class MySqlite(object):
    conn = None
    __config = None
    def __init__(self, config={}):
        # sqlite ./abc.db
        if not self.__config:
            self.__config = {
                'database': "example.db",
                'timeout': 5.0,
                'detect_types': 0,
                # 'isolation_level': None,
                'check_same_thread': True, # 是否检测调用在同一线程
                # 'factory': None,
                # 'cached_statements': 100,
            }
            self.__config.update(config)
        self.conn = self.__get_connection()

    def __del__(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, type, value, trace):
        self.cursor.close()

    def __get_connection(self):
        if self.conn:
            return self.conn
        return sqlite3.connect(database=self.__config['database'], check_same_thread=self.__config['check_same_thread'])

    def commit( self ):
        return self.conn.commit()
    def rollback( self ):
        return self.conn.rollback()

    def select( self, sql, data_tuple=None ):
        """ return: rows dict """
        self.execute(sql, data_tuple)
        return self.cursor.fetchall() # 若要返回单条: fetchone

    def execute( self, sql, data_tuple=None ):
        if not data_tuple:
            return self.cursor.execute( sql )
        else:
            return self.cursor.execute( sql, data_tuple )

def _DictFactory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

if __name__ == "__main__":
    from mysqlite2 import MySqlite
    import traceback

    config = {
        'database': "example.db",
        'timeout': 5.0,
        'detect_types': 0,
        # 'isolation_level': None,
        'check_same_thread': True, # 是否检测调用在同一线程
        'factory': _DictFactory,
        # 'cached_statements': 100,
    }
    def test_create():
        with MySqlite(config) as p:
            try:
                sql = """
                CREATE TABLE IF NOT EXISTS `up_task` (
                    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
                    `add_time` TEXT,
                    `info_hash` TEXT default 99,
                    `owner` TEXT,
                    UNIQUE (info_hash, owner)
                );
                """
                p.execute(sql)
                ret = p.commit()
                print ret # None
            except:
                p.rollback()
                print traceback.format_exc()

    def test_insert():
        with MySqlite(config) as p:
            try:
                # sql = "vacuum"
                p.execute('insert into up_task(add_time, info_hash, owner) values(?, ?, ?)',
                    ('add_time', '1', 'zlx')
                )
                ret = p.commit()
                print ret # None
            except:
                p.rollback()
                print traceback.format_exc()

    def test_select():
        with MySqlite(config) as p:
            # 系统表: sqlite_master
            rows = p.select('select * from up_task')
            print rows # [(1, u'add_time', u'1', u'zlx')]

if __name__ == "__main__":
    def Usage():
        print u"""
        python ./{0} test_create
        python ./{0} test_insert
        python ./{0} test_select
        """.format(os.path.basename(__file__))
    import sys, os
    if len(sys.argv) == 1: Usage(), sys.exit()
    function = sys.argv[1]
    del sys.argv[1]
    eval(function)()
