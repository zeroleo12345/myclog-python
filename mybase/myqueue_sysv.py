#!/usr/bin/python
#coding:utf-8
"""
    systemV消息队列 | posix消息队列 区别:
        1. systemV消息队列 send recv 不支持超时(需配合signal.alarm), 只支持 阻塞 | 非阻塞

    reference:
        http://semanchuk.com/philip/sysv_ipc/
        http://www.linuxidc.com/Linux/2011-10/44830.htm
    queue example:
        sysv_ipc-0.6.8/demo2
        premise.py,  conclusion.py, params.txt
"""

import signal
import os
import sysv_ipc

class SignalError(Exception):
    pass
class TimeoutError(Exception):
    pass

def alarm_timeout(signum, frame):
    raise TimeoutError('alarm timeout')

class MyQueue():
    def __init__(self, name, id=42, flag=sysv_ipc.IPC_CREAT, mode=0600, msgmax=2048, destroy=0):
        """
        destroy: 1 unlink queue when close()
        MessageQueue( key, [flags = 0, mode = 0600, max_message_size = 2048] )
        flags set to the default of 0, attempts to open an existing message queue identified by key and raises a ExistentialError if it doesn't exist.
        flags set to IPC_CREAT, opens the message queue identified by key or creates a new one if no such queue exists.
        flags set to IPC_CREX (IPC_CREAT | IPC_EXCL), creates a new message queue identified by key. If a queue with that key already exists, the call raises a ExistentialError.
        """
        if not os.path.exists( name ): raise Exception( 'queue file:%s not exist' % name )
        # name: /root/115/code/etc/g_115_acct_proc_queue
        self.destroy = destroy
        self.name = name
        key = sysv_ipc.ftok(self.name, id, silence_warning = True)
        if key < 0: raise Exception('ftok error.name:%s'%self.name)
        self.mq = sysv_ipc.MessageQueue( key, flag, mode, msgmax )

    def send(self, msg, timeout=None, type=1):
        """ params:
                timeout == None 阻塞
                timeout <= 0, 马上返回, 发送失败时raise BusyError
                timeout > 0, 等待n秒, 发送失败raise BusyError
                block: specifies whether should wait if the message can't be sent (if, for example, the queue is full).
                        When block is False, will raise a BusyError if the message can't be sent immediately
                type: must be > 0
            return: None. if Success
                    raise Exception. when Error
        """
        try:
            if timeout <= 0: # 马上返回, timeout <= 0
                block = False
                self.mq.send( msg, block, type )
            elif timeout > 0: # 超时时间内返回, timeout > 0
                signal.signal(signal.SIGALRM, alarm_timeout) # 注册信号处理函数
                signal.alarm( timeout )
                block = True
                self.mq.send( msg, block, type )
                signal.alarm(0)  # 删除信号
            elif timeout is None: # 阻塞发, timeout==None
                block = True
                self.mq.send( msg, block, type )
            else: raise Exception('param error')
        except sysv_ipc.BusyError as e: # When block is False, the call will raise a BusyError if a message can't be received immediately
            raise TimeoutError('send timeout.queue is empty')
        except sysv_ipc.Error as e:
            if str(e) == 'Signaled while waiting': raise SignalError( str(e) ) # 判断是否信号中断
            else: raise e

    def recv(self, timeout=None, type=0):
        """ params:
                timeout = None, block receive
                timeout = 0, return immediately
                timeout > 0, wait for seconds

                type = 0, returns first message regardless of its type.
                type > 0, returns first message of type.
                type < 0, returns first message of lowest type which is ≤  |type|.
            return: (message, type)
        """
        try:
            if timeout == 0: # 马上返回
                block = False
                return self.mq.receive(block, type)
            elif timeout is None: # 阻塞读
                block = True
                return self.mq.receive(block, type)
            else: # 超时时间内返回
                signal.signal(signal.SIGALRM, alarm_timeout) # 注册信号处理函数
                signal.alarm( timeout )
                block = True
                ret = self.mq.receive(block, type)
                signal.alarm(0)  # 删除信号
                return ret
        except sysv_ipc.BusyError as e: # When block = False, the call will raise a BusyError if a message can't be received immediately
            raise TimeoutError('receive timeout.queue is empty')
        except sysv_ipc.Error as e:
            if str(e) == 'Signaled while waiting': raise SignalError( str(e) ) # 判断是否信号中断
            else: raise e

    def close(self):
        if self.destroy: self._unlink()

    def _unlink(self):
        self.mq.remove()

    """ 静态方法 """
    @staticmethod
    def unlink_static( id ):
        """ Params:
                (MessageQueue Object).id
        """
        sysv_ipc.remove_message_queue( id )

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

    def close(self, key):
        for v in self.values(): v.close()

""" GLOBAL """
g_queue_pool = MyQueuePool()

if __name__ == '__main__':
    import traceback
    import time
    from mybase.myqueue_sysv import MyQueue, TimeoutError, SignalError
    from mybase.mysignal import g_signal

    def test_send():
        queue_file = os.path.join( './', os.path.basename(__file__) )
        outqueue = MyQueue(name = queue_file, destroy=0)
        try:
            start = None
            msg = os.urandom(1024)
            for i in xrange(0, 1):
                try: outqueue.send( msg, timeout=30, type=1 )
                except SignalError: continue
                if start is None:
                    start = time.time()
                    print start
                    print msg.encode('hex')
            end = time.time()
            print end 
            print 'use time %s second' % ( end-start, )
        except TimeoutError as e:
            print "%s" % traceback.format_exc()
        except Exception as e:
            print "%s" % traceback.format_exc()
        finally:
            outqueue.close() # MyQueue.unlink_static( outqueue.id )

    def test_recv():
        queue_file = os.path.join( './', os.path.basename(__file__) )
        g_signal.register()
        inqueue = MyQueue(name = queue_file, destroy=0)
        try:
            start = None
            #while not g_signal.term:
            for i in xrange(0, 100000):
                #print 'recving'
                try: (msg, _type) = inqueue.recv( timeout=None, type=0 )
                except SignalError: continue
                #print 'msg:%s, type:%d' % (msg, _type)
                if start is None:
                    start = time.time()
                    print start
                    print msg.encode('hex')
            end = time.time()
            print end 
            print 'use time %s second' % ( end-start, )
        except TimeoutError as e:
            print "%s" % traceback.format_exc()
        except Exception as e:
            print "%s" % traceback.format_exc()
        finally:
            inqueue.close() # MyQueue.unlink_static( inqueue.id )

    def queue_key():
        filepath = sys.argv[1]
        key = sysv_ipc.ftok(filepath, id=42, silence_warning = True)
        result = hex(int(key))
        print 'key:', result

        command = 'ipcs -q | grep %s' % ( result, )
        os.system( command )

if __name__ == '__main__':
    def Usage():
        print u"""
        python ./{0} test_recv
        python ./{0} test_send
        结论:
            1. python纯收发Queue 1024字节消息, 十万个消息耗时0.60秒 (VMware CPU i3 3.4GHz, 8G memory)

        # 查看msgid:  ipcs -q
            ./myqueue_sysv.py queue_key /root/code/baicai/wxservice/release/queue/SyncRoomInfo
        """.format(os.path.basename(__file__))
    import sys, os
    if len(sys.argv) == 1: Usage(), sys.exit()
    function = sys.argv[1]
    del sys.argv[1]
    eval(function)()
