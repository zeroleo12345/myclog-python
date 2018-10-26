#!/usr/bin/python
#coding:utf-8

""" Reference: (进程间互斥锁)
        http://www.redicecn.com/html/Python/20131108/464.html
"""

import os
try:
    import fcntl
    LOCK_EX = fcntl.LOCK_EX
except ImportError:
    # Windows平台下没有fcntl模块
    fcntl = None
    try:
        import win32con # pypiwin32
    except ImportError as e:
        print """
        need module: pip install pypiwin32
        """
        raise e
    import win32file
    import pywintypes
    LOCK_EX = win32con.LOCKFILE_EXCLUSIVE_LOCK
    overlapped = pywintypes.OVERLAPPED()

class MyMutex:
    def __init__(self, filepath='.process_lock'):
        """ 用于阻塞读取单个资源
        """
        self.filepath = filepath
        self.fd = open(filepath, 'w') # 如果文件不存在则创建

    def __del__(self):
        try:
            self.fd.close()
            os.remove(self.filepath) # 退出时, 自动清理文件
        except:
            pass

    def acquire(self):
        # 给文件上锁
        if fcntl:
            fcntl.flock(self.fd, LOCK_EX)
        else:
            hfile = win32file._get_osfhandle(self.fd.fileno())
            win32file.LockFileEx(hfile, LOCK_EX, 0, -0x10000, overlapped)

    def release(self):
        # 文件解锁
        if fcntl:
            fcntl.flock(self.fd, fcntl.LOCK_UN)
        else:
            hfile = win32file._get_osfhandle(self.fd.fileno())
            win32file.UnlockFileEx(hfile, 0, -0x10000, overlapped)

if __name__ == '__main__':
    def test_lock():
        import time
        print 'start time: %s' % time.time()
        lock = MyMutex()
        try:
            lock.acquire()
            time.sleep(5)
        finally:
            lock.release()
        print 'stop  time: %s' % time.time()

if __name__ == '__main__':
    def Usage():
        print """
        ./mymutex.py test_lock
        测试方法: 依次运行本程序多个实例，第N个实例运行耗时是第一个的N倍
        """
    import sys, os, pdb
    if len(sys.argv) == 1: Usage(), sys.exit()
    function = sys.argv[1]
    del sys.argv[1]
    eval(function)()
