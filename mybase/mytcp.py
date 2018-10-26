#!/usr/bin/python
#coding:utf-8
""" Reference:
        socket:
            https://docs.python.org/2/library/socket.html
            http://blog.csdn.net/rebelqsp/article/details/22109925
            https://docs.python.org/2/howto/sockets.html

        errno:
            https://docs.python.org/2/library/errno.html#module-errno
            SEE ALL ERRNO: print errno.errorcode

        select:     ( 用于轮询多个fd是否可读, 可写, 或者异常 )
            https://docs.python.org/2/library/select.html#select.select
"""

import socket
import errno
import time
import platform

class SocketTimeout(Exception):
    pass
class SocketClose(Exception):
    pass
class SocketError(Exception):
    pass

class MyTcp():
    if 'Linux' in platform.system():
        AF_UNIX = socket.AF_UNIX
        MSG_DONTWAIT = socket.MSG_DONTWAIT
        MSG_WAITALL = socket.MSG_WAITALL
    AF_INET = socket.AF_INET
    AF_INET6 = socket.AF_INET6
    SOL_SOCKET = socket.SOL_SOCKET
    SO_REUSEADDR = socket.SO_REUSEADDR
    SOCK_STREAM = socket.SOCK_STREAM

    def __init__( self, family=AF_INET, type=SOCK_STREAM, proto=0 ):
        self.family = family
        self.sock = socket.socket( family, type )

    if 'Linux' in platform.system():
        def recv_nowait( self, bufsize=1024 ):
            """
            self.sock.setblocking( 0 ) # 0-非阻塞, 1-阻塞
                setblocking(1)  ==  settimeout(None)
                setblocking(0)  ==  settimeout(0.0)
                非阻塞下, 没有数据读或不能马上写, raise socket.error
            self.sock.settimeout( 0 ) # 设置超时时间为0, 效果与非阻塞相像
                settimeout(None) ==: setblocking(1)
                settimeout(0) ==: setblocking(0)
                超时则, raise socket.timeout
            """
            try:
                _r = self.sock.recv( bufsize, socket.MSG_DONTWAIT ) # flags=socket.MSG_DONTWAIT
                if not _r: # TCP不会发送0长度的包. 实际用于判断断开连接的是FIN包; PY返回'', C返回长度为0
                    raise SocketClose('socket is closed')
                return _r
            except socket.error as e:
                (errnum, err_msg) = e 
                if errnum == errno.EAGAIN: # [Errno 11] Resource temporarily unavailable 
                    return '' # 没有数据可读. 可优化为先用select轮询fd是否可读
                else: raise SocketError( "recv_nowait error: %s, errnum=%d" % (err_msg, errnum) )

    def recv_one_packet( self, bufsize=1024 ):
        """ flags:
                0 - 无论阻塞或非阻塞, 都是读到就返回
                MSG_WAITALL - 阻塞下读够bufsize才返回; 非阻塞下,未读够bufsize字节返回<0
        """
        while 1:
            try:
                _r = self.sock.recv( bufsize ) # flags
                if not _r: # TCP不会发送0长度的包. 实际用于判断断开连接的是FIN包; PY返回'', C返回长度为0
                    raise SocketClose('socket is closed')
                return _r
            except socket.error as e:
                (errnum, err_msg) = e 
                if errnum == errno.EINTR: continue
                else: raise SocketError( "recv_one_packet error: %s, errnum=%d" % (err_msg, errnum) )

    def sendall( self, msg ):
        """ return:
            success: None
            fail: raise an exception
        """
        return self.sock.sendall( msg )

    def recvn( self, nExpectLen, nTimeout ):
        """ params:
                nTimeout: seconds
            return:
                data: binary str, and len(data) > 0
            exception:
                SocketTimeout, SocketError, SocketClose
        """
        nReadLen = 0 
        data = []
        try:
            self.sock.settimeout( nTimeout )
            while nReadLen < nExpectLen:
                try:
                    _r = self.sock.recv( nExpectLen - nReadLen )
                    if not _r: # TCP不会发送0长度的包. 实际用于判断断开连接的是FIN包; PY返回'', C返回长度为0
                        raise SocketClose('socket is closed')
                    data.append( _r )
                    nReadLen += len( _r )
                except socket.timeout as e:
                    raise SocketTimeout("recvn timeout: nExpectLen=%d, nReadLen=%d" % (nExpectLen, nReadLen))
                except socket.error as e:
                    (errnum, err_msg) = e 
                    if errnum == errno.EINTR: continue
                    else: raise SocketError( "recvn error: %s, errnum=%d" % (err_msg, errnum) )
            return ''.join(data)
        finally:
            self.sock.settimeout( None ) # 使设置失效

    def sendn( self, msg, nExpectLen, nTimeout ):
        """ params:
                msg: binary str
                nTimeout: seconds
            return: (nWriteLen, reason)
                success: nWriteLen > 0, and reason = ''
                fail: nWriteLen < 0, and reason is str
        """
        nWriteLen = 0 
        try:
            self.sock.settimeout( nTimeout )
            while nWriteLen < nExpectLen :
                try:
                    #发送时,若对端断开连接, send不知道状>    态,且永远成功. 要获取断开状态需配合select
                    _s_len = self.sock.send( msg[nWriteLen:nExpectLen] )
                    nWriteLen += _s_len;
                except socket.timeout as e:
                    raise SocketTimeout("sendn timeout: nExpectLen=%d, nWriteLen=%d" % (nExpectLen, nWriteLen))
                except socket.error as e:
                    (errnum, err_msg) = e 
                    if errnum == errno.EINTR: continue
                    else: raise SocketError( "sendn error: %s, errnum=%d" % (err_msg, errnum) )
            return ( nWriteLen, '' )
        finally:
            self.sock.settimeout( None ) # 使设置失效

    def setsockopt(self, level, optname, value):
        self.sock.setsockopt( level, optname, value )

    def bind(self, ip, port):
        """ socket.bind( address ) params:
                AF_UNIX family: str. 用于UNIX域套接字
                AF_INET family: (host, port). 用于IPV4
                AF_INET6 family: (host, port, flowinfo, scopeid).
        """
        if self.family == self.AF_INET:
            self.sock.bind( (ip, port) )
        else: raise Exception('unknow socket family')

    def listen(self, backlog):
        """ params:
                backlog: 在调用accept方法取出连接时，能接受的最大连接数 
        """
        self.sock.listen( backlog )

    def accept(self):
        """ return: (conn, address)
                conn: socket对象用于收发消息
                address: is the address bound base on family family
        """
        if self.family == self.AF_INET:
            ( conn, (ip, port) ) = self.sock.accept()
            return ( conn, (ip, port) )
        else: raise Exception('unknow socket family')

    def connect(self, ip, port, maxtry=1):
        """ return:
                fail: raise SocketError
        """
        for i in xrange(0, maxtry):
            try:
                self.sock.connect( (ip, int(port)) )
                return   # return if success
            except socket.error as e:
                time.sleep(0.01)
            raise SocketError( 'try %d times but connect fail' % maxtry )

    def close(self):
        if self.sock:
            self.sock.close()
        self.sock = None
"""
inputs = [mytcp.sock]
outputs = []
timeout = 0 # 0-非阻塞
while 1:
    readable, writeable, exceptional = select.select(inputs, outputs, inputs, timeout)
    print '123'
    if not (readable or writeable or exceptional):
        print 'Time Out!'
        break
    else:
        print 'Socket not Empty'
    if mytcp.tcp in readable:
        mytcp.recv()
"""

if __name__ == "__main__":
    def test_server_accept_and_recv():
        try:
            ip = '127.0.0.1'
            port = 6000
            mytcp = MyTcp(family=MyTcp.AF_INET, type=MyTcp.SOCK_STREAM)
            mytcp.setsockopt( MyTcp.SOL_SOCKET, MyTcp.SO_REUSEADDR, 1 )
            mytcp.bind( ip, port )
            mytcp.listen( backlog=1 )
            ( conn, (ip, port) ) = mytcp.accept()
            try:
                print 'Connected by', ip, port
                data = conn.recv(1024)
                if not data: print 'data is None'
                else: print 'recv data: %s. data len:%s' % ( data, len(data) )

                conn.sendall(data)
                print 'send data:', data
            finally:
                conn.close()
        finally:
            mytcp.close()

    def test_client_sendn_and_recvn():
        try:
            ip = '127.0.0.1'
            port = 6000
            maxtry = 1
            mytcp = MyTcp(family=MyTcp.AF_INET, type=MyTcp.SOCK_STREAM)
            mytcp.setsockopt( MyTcp.SOL_SOCKET, MyTcp.SO_REUSEADDR, 1 )
            mytcp.connect( ip, port, maxtry )
            msg = '123'
            msglen = len(msg)
            (nlen, reason) = mytcp.sendn( msg, nExpectLen=msglen, nTimeout=10 )
            print 'send data:', msg

            data = mytcp.recvn( nExpectLen=msglen, nTimeout=10 )
            print 'recv data: %s. data len:%s' % ( data, len(data) )
        finally:
            mytcp.close()

    def test_client_sendall_and_recv_nowait():
        try:
            ip = '127.0.0.1'
            port = 6000
            maxtry = 1
            mytcp = MyTcp(family=MyTcp.AF_INET, type=MyTcp.SOCK_STREAM)
            mytcp.setsockopt( MyTcp.SOL_SOCKET, MyTcp.SO_REUSEADDR, 1 )
            mytcp.connect( ip, port, maxtry )
            msg = '123'
            msglen = len(msg)
            mytcp.sendall( msg )
            print 'send data:', msg

            """ recv_nowait """
            data = mytcp.recv_nowait( bufsize=1024 )
            print 'recv data: %s. data len:%s' % ( data, len(data) )
        finally:
            mytcp.close()

    def test_client_sendall_and_recv_one_packet():
        try:
            ip = '127.0.0.1'
            port = 6000
            maxtry = 1
            mytcp = MyTcp(family=MyTcp.AF_INET, type=MyTcp.SOCK_STREAM)
            mytcp.setsockopt( MyTcp.SOL_SOCKET, MyTcp.SO_REUSEADDR, 1 )
            mytcp.connect( ip, port, maxtry )
            msg = '123'
            msglen = len(msg)
            mytcp.sendall( msg )
            print 'send data:', msg

            """ recv_one_packet """
            data = mytcp.recv_one_packet( bufsize=1024 )
            print 'recv data: %s. data len:%s' % ( data, len(data) )
        finally:
            mytcp.close()

if __name__ == "__main__":
    def Usage():
        print """ 
        ./mytcp.py test_server_accept_and_recv
        ./mytcp.py test_client_sendn_and_recvn
        ./mytcp.py test_client_sendall_and_recv_nowait
        ./mytcp.py test_client_sendall_and_recv_one_packet
        """
    import sys, os, pdb 
    if len(sys.argv) == 1: Usage(), sys.exit()
    function = sys.argv[1]
    del sys.argv[1]
    eval(function)()
