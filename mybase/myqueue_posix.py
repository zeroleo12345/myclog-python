#!/usr/bin/python
#coding:utf-8
import posix_ipc

'''
    systemV消息队列 | posix消息队列 区别:
        1. systemV消息队列 send recv 不支持超时, 只支持 阻塞 | 非阻塞

    reference:
        http://semanchuk.com/philip/posix_ipc/
    queue example:
        posix_ipc-1.0.0/demo2
        premise.py,  conclusion.py, params.txt
'''

from posix_ipc import SignalError
class TimeoutError(Exception):
    pass

class MyQueue():
    def __init__(self, name, flag=posix_ipc.O_CREAT, mode=0600, destroy=0):
        """
        MessageQueue(name, flags = 0, mode = 0600, 
                    max_messages = QUEUE_MESSAGES_MAX_DEFAULT, max_message_size = QUEUE_MESSAGE_SIZE_MAX_DEFAULT, 
                    read = True, write = True)
        flags default of 0, attempts to open an existing queue and raises an error if that queue doesn't exist.
        flags O_CREAT, opens the queue if it exists (in which case size and mode are ignored) or creates it if it doesn't.
        flags O_CREAT | O_EXCL (or O_CREX), creates a new message queue identified by name. If a queue with that name already exists, the call raises an ExistentialError.
        """
        # name example: /g_115_acct_proc_queue
        self.destroy = destroy
        self.name = name
        self.mq = posix_ipc.MessageQueue( name, flag, mode )

    def send(self, msg, timeout=None, priority=0):
        """ timeout == None 阻塞
            timeout == 0, 马上返回, 发送失败时raise BusyError
            timeout > 0, 等待n秒, 发送失败raise BusyError
        """
        self.mq.send( msg, timeout, priority )

    def recv(self, timeout=None):
        """ return: (message, priority) """
        try:
            return self.mq.receive(timeout)
        except posix_ipc.BusyError as e: # timeout
            raise TimeoutError('recv timeout')

    def close(self):
        self.mq.close()
        if self.destroy: self._unlink()

    def _unlink(self):
        self.mq.unlink()

    """ 静态方法 """
    @staticmethod
    def unlink_static( name ):
        posix_ipc.unlink_message_queue( name )

class MyQueuePool(dict):
    def __getitem__(self, key):
        return dict.__getitem__(self, key)

    def __contains__(self, key):
        try:
            return dict.__contains__(self, key)
        except KeyError:
            return False

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise Exception('key is not str')
        if not isinstance(value, MyQueue):
            raise Exception('value is not MyQueue')
        dict.__setitem__(self, key, value)

    def close(self):
        for v in self.values(): v.close()

if __name__ == '__main__':
    import traceback
    from mybase.myqueue_posix import MyQueue, TimeoutError
    from mybase.mysignal import g_signal
    from etc.global_conf import *

    def test_recv():
        g_signal.register()
        queue = MyQueue(name=g_115_acct_proc_queue, destroy=0)
        try:
            while not g_signal.term:
                (msg, pri) = queue.recv()
        except TimeoutError as e:
            print "%s" % traceback.format_exc()
        except Exception as e:
            print "%s" % traceback.format_exc()
        finally:
            queue.close()

    def test_unlink_static():
        """
        Usage: 
            ./myqueue_prosix.py test_unlink_static g_website_proc_queue5508
        """
        import sys
        queue_name = '/' + sys.argv[1]
        MyQueue.unlink_static( queue_name )

    def test_queue_pool():
        queue_pool = MyQueuePool()

if __name__ == '__main__':
    function = sys.argv[1]
    del sys.argv[1]
    eval(function)()
