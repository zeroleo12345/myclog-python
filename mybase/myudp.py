#!/usr/bin/python
#coding:utf-8

"""
    Reference:
        Socket:
            https://docs.python.org/2/library/socket.html
            http://blog.csdn.net/rebelqsp/article/details/22109925
            https://docs.python.org/2/howto/sockets.html

        errno:
            https://docs.python.org/2/library/errno.html#module-errno
"""
import socket
import errno

class SignalError(Exception):
    pass
class TimeoutError(Exception):
    pass

class MyUdp():
    def __init__(self, maxlen=1024):
        self.maxlen = maxlen
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def bind(self, ip, port):
        """ ip: 0.0.0.0 bind all interface """
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind( (ip, port) )

    def close(self):
        self.sock.close()

    def recv(self, flags=socket.MSG_WAITALL):
        """ return: msg """
        try:
            msg = self.sock.recv(self.maxlen, flags) # socket.MSG_DONTWAIT
            return msg
        except Exception as e:
            (errnum, err_msg) = e 
            if errnum == errno.EINTR: raise SignalError( err_msg ) # 判断是否信号中断
            else: raise e

    def recvfrom(self, flags=socket.MSG_WAITALL):
        """ return: ( msg, (ip, port) ) """
        try:
            msg = self.sock.recvfrom(self.maxlen, flags) # socket.MSG_DONTWAIT
            return msg
        except Exception as e:
            (errnum, err_msg) = e 
            if errnum == errno.EINTR: raise SignalError( err_msg ) # 判断是否信号中断
            else: raise e

    def sendto(self, ip, port, msg):
        self.sock.sendto( msg, (ip, port) )

if __name__ == '__main__':
    import time
    import os
    def init_args():
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('-sleep', metavar='<seconds>', type=int, default=0, help='sleep second', required=False)
        parser.add_argument('-ip', metavar='<ip>', type=str, help='ip', required=True)
        parser.add_argument('-port', metavar='<port>', type=int, help='port', required=True)
        parser.add_argument('-times', metavar='<port>', type=int, default=0, help='send times', required=False)
        return parser.parse_args()

    #def testRecv(ip, port, times):
    def testRecv():
        args = init_args()
        recver = MyUdp(args.times)
        recver.bind(args.ip, args.port)
        start = None
        pkt_cnt = 0
        end_cnt = 0
        while 1:
            (msg, (args.ip, args.port)) = recver.recvfrom() # (msg, (args.ip, args.port))
            pkt_cnt += 1
            recv_cnt = 1
            if len(msg) > 300:
                end_cnt += 1
                if end_cnt == args.times: break
            if start is None:
                start = time.time()
                print start
                print 'msg:%s, len:%s' % ( msg.encode('hex'), len(msg) )
            if pkt_cnt % 10000 == 0: print pkt_cnt
        end = time.time()
        print end
        print 'use time %s second' % ( end-start, )
        print 'pkt_cnt %s' % pkt_cnt
    
    #def testSend(ip, port, times):
    def testSend():
        args = init_args()
        sender = MyUdp()
        start = None
        msg = str(time.time())[-1] + os.urandom(300)
        for i in xrange(0, args.times):
            if i == args.times-1: sender.sendto(args.ip, args.port, os.urandom(400))
            else: sender.sendto(args.ip, args.port, msg)
            if args.sleep: time.sleep(args.sleep)
            if start is None:
                start = time.time()
                print start
                print msg.encode('hex')
        end = time.time()
        print end
        print 'use time %s second' % ( end-start, )

if __name__ == '__main__':
    def Usage():
        print u"""
        ./myudp.py testRecv -ip 127.0.0.1 -port 1812 -times 1000000
        ./myudp.py testSend -ip 127.0.0.1 -port 1812 -times 1000000 -sleep 0
        结论:
            1. python纯收发UDP 1024字节消息, 十万个消息耗时1.19秒 (VMware CPU i3 3.4GHz, 8G memory)
        """
    import sys 
    if len(sys.argv) == 1: Usage(), sys.exit()
    function = sys.argv[1]
    del sys.argv[1]
    eval(function)()
