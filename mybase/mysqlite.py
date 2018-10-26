#!/usr/bin/env python
#coding:utf-8
import os
import sys
import sqlite3

_g_conn = {}
def Connect(db):
    global _g_conn
    if not _g_conn.has_key(db):
        _g_conn[db] = sqlite3.connect(db, check_same_thread = False)
    return _g_conn[db]

def Close():
    global _g_conn
    for key in _g_conn:
        _g_conn[key].close()

''' private '''
def _DictFactory(cursor, row):  
    d = {}  
    for idx, col in enumerate(cursor.description):  
        d[col[0]] = row[idx]  
    return d 

''' type(data) == tuple. like: data = (1,2,) '''
''' len(records) '''
def Select(db_path, sql, data=None):
    conn = Connect(db_path)
    conn.row_factory = _DictFactory
    cur = conn.cursor()
    if data is None:
        cur.execute(sql)
    else:
        cur.execute(sql, data)
    records = cur.fetchall()  # fetchone
    return records

''' type(data) == tuple. like: data = (1,2,) '''
def Insert(db_path, sql, data):
    conn = Connect(db_path)
    cu = conn.cursor()
    cu.execute(sql, data)
    conn.commit()
    cu.close()

''' type(data) == tuple. like: data = (1,2,) '''
def Update(db_path, sql, data):
    conn = Connect(db_path)
    cu = conn.cursor()
    cu.execute(sql, data)
    conn.commit()
    cu.close()

''' select count(*) from sqlite_master where type='table' and name='table_XXX' '''
def Create(db_path, sql):
    conn = Connect(db_path)
    cu = conn.cursor()
    cu.execute(sql)
    conn.commit()
    cu.close()

if __name__ == "__main__":
    def test_execute_vacuum():
        db_path = "./decrypted_database.db"
        sql = "vacuum"
        conn = Connect(db_path)
        cu = conn.cursor()
        cu.execute(sql)
        conn.commit()
        cu.close()

if __name__ == "__main__":
    def Usage():
        print u"""
        python ./{0} test_execute_vacuum
        """.format(os.path.basename(__file__))
    import sys, os
    if len(sys.argv) == 1: Usage(), sys.exit()
    function = sys.argv[1]
    del sys.argv[1]
    eval(function)()
