#!/usr/bin/python
#coding:utf-8
import sysv_ipc

""" Reference:
        http://semanchuk.com/philip/sysv_ipc/
    queue example:
        sysv_ipc-0.6.8/demo
        premise.py,  conclusion.py, params.txt
"""

from sysv_ipc import ExistentialError
class TimeoutError(Exception):
    pass

ID = 42
IPC_CREX = sysv_ipc.IPC_CREX
class MySemaphore():
    def __init__(self, path, id=ID, flag=IPC_CREX, mode=0600, value=0):
        """ 用于多进程里多个资源分享
        Semaphore( key, [flags = 0, mode = 0600, initial_value = 0] )
        flags default of 0, open an existing semaphore and raises an error if that semaphore doesn't exist.
        flags set to IPC_CREAT, the module opens the semaphore identified by key or creates a new one if no such semaphore exists.
        flags set to IPC_CREX (IPC_CREAT | IPC_EXCL), the module creates a new semaphore identified by key. If a semaphore with that key already exists, the call raises an ExistentialError. initial_value is ignored unless both of these flags are specified or if the semaphore is read-only
        """
        # path: /root/115/code/etc/g_115_acct_proc_sem
        key = sysv_ipc.ftok(path, id, silence_warning = True)
        if key < 0: raise Exception('ftok error.path:%s'%path)
        self.sem = sysv_ipc.Semaphore( key, flag, mode, initial_value=value )

    def acquire(self, timeout=None, delta=1):
        """ decrementing the semaphore """
        try:
            self.sem.acquire( timeout, delta )
        except sysv_ipc.BusyError as e: # timeout
            raise TimeoutError('acquire timeout') # The queue is empty

    def release(self, delta = 1):
        """ increments the semaphore """
        self.sem.release(delta)

    def unlink(self):
        self.sem.remove()

    @staticmethod
    def unlink_static( sem ):
        """ 静态方法
        Params: Semaphore Object """
        sysv_ipc.remove_semaphore(sem.id)

def global_unlink():
    g_sem.unlink()

if __name__ == '__main__':
    """ HOW TO USE """
    from etc.global_conf import g_115_acct_proc_sem
    try:
        g_sem = MySemaphore(path=g_115_acct_proc_sem, id=mybase.mysemaphore_sysv.ID, flag=mybase.mysemaphore_sysv.IPC_CREX, mode=0600, value=1)
    except ExistentialError as e:
        print 'g_sem Exist.path:%s, id=%d' % (g_115_acct_proc_sem, mybase.mysemaphore_sysv.ID)
        g_sem = MySemaphore(path=g_115_acct_proc_sem, id=mybase.mysemaphore_sysv.ID, flag=0)

if __name__ == '__main__':
    from mybase.mysignal import g_signal
    import time, os, sys

    def testAcquire():
        g_signal.register()
        try:
            while not g_signal.term:
                print(os.getpid(), 'Acquiring read lock')
                print g_sem.acquire(timeout=0.1, delta=1)
                print(os.getpid(), 'Sleeping for a while')
                time.sleep(10)
                print(os.getpid(), 'Releasing lock')
                g_sem.release(delta=1)
        except TimeoutError as e:
            print 'TimeoutError'
            print e
        except Exception as e:
            print 'Exception'
            print e
        finally:
            pass
            #g_sem.unlink()

    def test_recv_sem():
        if len(sys.argv) > 1:
            global_unlink()
        else:
            testAcquire()

    function = sys.argv[1]
    del sys.argv[1]
    eval(function)()
