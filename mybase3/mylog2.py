# coding:utf-8
import myclog
from mybase3.ilog import ILog
import traceback

class MyLog(ILog):
    def __init__(self):
        super(self.__class__, self).__init__()

    @staticmethod
    def setLogHeader(header='prefix'):
        myclog.setLogHeader(header)

    @staticmethod
    def setLogDir(log_dir='./'):
        myclog.setLogDir(log_dir)

    @staticmethod
    def setLogBufferSize(buff_size=10240):
        myclog.setLogBufferSize(buff_size)

    @staticmethod
    def setLogMaxLine(max_line=100000):
        myclog.setLogMaxLine(max_line)

    @staticmethod
    def setLogLevel(level='debug'):
        myclog.setLogLevel(level)

    @staticmethod
    def flush():
        myclog.flush()

    @staticmethod
    def close():
        myclog.close()

    @staticmethod
    def get_fileno():
        return myclog.get_fileno()

    @staticmethod
    def trace(fmt, *args, **kwargs):
        try:
            if kwargs.has_key('hook'): args = tuple(map(kwargs['hook'], args))
            if args: fmt = fmt % args
            myclog.trace(fmt)
        except Exception as e:
            print(args)
            print(kwargs)
            raise e

    @staticmethod
    def db(fmt, *args, **kwargs):
        try:
            if kwargs.has_key('hook'): args = tuple(map(kwargs['hook'], args))
            if args: fmt = fmt % args
            myclog.db(fmt)
        except Exception as e:
            print(traceback.format_exc())
            print(args)
            print(kwargs)
            raise e

    @staticmethod
    def info(fmt, *args, **kwargs):
        try:
            if kwargs.has_key('hook'): args = tuple(map(kwargs['hook'], args))
            if args: fmt = fmt % args
            myclog.info(fmt)
        except Exception as e:
            print(traceback.format_exc())
            print(args)
            print(kwargs)
            raise e

    @staticmethod
    def warn(fmt, *args, **kwargs):
        try:
            if kwargs.has_key('hook'): args = tuple(map(kwargs['hook'], args))
            if args: fmt = fmt % args
            myclog.warn(fmt)
        except Exception as e:
            print(traceback.format_exc())
            print(args)
            print(kwargs)
            raise e

    @staticmethod
    def error(fmt, *args, **kwargs):
        try:
            if kwargs.has_key('hook'): args = tuple(map(kwargs['hook'], args))
            if args: fmt = fmt % args
            myclog.error(fmt)
        except Exception as e:
            print(traceback.format_exc())
            print(args)
            print(kwargs)
            raise e

    @staticmethod
    def critical(fmt, *args, **kwargs):
        try:
            if kwargs.has_key('hook'): args = tuple(map(kwargs['hook'], args))
            if args: fmt = fmt % args
            myclog.critical(fmt)
        except Exception as e:
            print(traceback.format_exc())
            print(args)
            print(kwargs)
            raise e

    @staticmethod
    def println(fmt, *args, **kwargs):
        try:
            if kwargs.has_key('hook'): args = tuple(map(kwargs['hook'], args))
            if args: fmt = fmt % args
            myclog.println(fmt)
        except Exception as e:
            print(traceback.format_exc())
            print(args)
            print(kwargs)
            raise e

log = MyLog()


if __name__ == "__main__":
    def test_MyLog():
        #from mybase3.mylog2 import log
        log.setLogHeader("logprefix")
        log.setLogDir(".\\")
        log.setLogBufferSize(10240)
        log.setLogMaxLine(10240)
        log.setLogLevel("error")
        log.trace("log:trace")
    
    def test_myclog():
        import traceback
        import time
        import sys
        
        try:
            print('print dir(myclog):')
            print(dir(myclog))
            e = myclog.setLogHeader("logprefix")
            if e:
                
                print('print e:')
                print(e)
                
                print('print e.message')
                print(e.message)
            myclog.setLogDir(".\\")
            myclog.setLogBufferSize(10240)
            myclog.setLogMaxLine(10240)
            myclog.setLogLevel("error")
            start = time.time()
            cnt = 0
            while 1:
                myclog.trace("log:trace")
                myclog.db("log:debug")
                myclog.warn("log:warn")
                myclog.error("log:error")
                myclog.critical("log:critical") # 60
                cnt = cnt + 1
                MyLog.error("str:%s, int:%s", "abc", 1)
                #myclog.flush()
                if cnt == 100: # 60 byte * 100 < 10240, 分开两次写来测试是否使用到缓存
                    cnt = 0
                    time.sleep(3)
            end = time.time()
            #myclog.close()
            print(end - start)
        except:
            print(traceback.format_exc())

if __name__ == "__main__":
    def Usage():
        print(u"""
        python3 ./{0} test_myclog
        python3 ./{0} test_MyLog
        """.format(__file__))
    import sys
    if len(sys.argv) == 1: Usage(), sys.exit()
    function = sys.argv[1]
    del sys.argv[1]
    eval(function)()
