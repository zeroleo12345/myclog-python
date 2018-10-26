#!/usr/bin/python
#coding:utf-8
import signal

class MySignal:
    @property
    def term(self):
        return self._term

    _term = False
    def _sig_handler(self, sig, frame):
        if sig in [signal.SIGINT, signal.SIGTERM]:
            self._term = True

    def register(self):
        """ 注册信号 """
        signal.signal(signal.SIGINT,    self._sig_handler)
        signal.signal(signal.SIGTERM,   self._sig_handler)
        #signal.signal(signal.SIGUSR1,  self._sig_handler)

""" GLOBAL """
g_signal = MySignal()

if __name__ == '__main__':
    from mybase.mysignal import g_signal
    
    def test_recv_signal():
        import time
        # 注册信号
        g_signal.register()
        while not g_signal.term:
            time.sleep(1)
            pass

if __name__ == '__main__':
    function = sys.argv[1]
    del sys.argv[1]
    eval(function)()
