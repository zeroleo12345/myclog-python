# coding:utf-8
from __future__  import print_function
import myclog
from mybase3.ilog import ILog
import traceback

class MyLog(ILog):
    def __init__(self):
        super(self.__class__, self).__init__()

    def init(self, header, directory, level, max_buffer=10240, max_line=100000):
        log.setLogHeader(header)
        log.setLogDir(directory)
        log.setLogLevel(level)
        log.setLogMaxBuffer(max_buffer)
        log.setLogMaxLine(max_line)

    @staticmethod
    def setLogHeader(header='prefix'):
        myclog.setLogHeader(header)

    @staticmethod
    def setLogDir(log_dir='./'):
        myclog.setLogDir(log_dir)

    @staticmethod
    def setLogMaxBuffer(buff_size=10240):
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
    def t(fmt, *args, **kwargs):
        try:
            if 'hook' in kwargs: args = tuple(map(kwargs['hook'], args))
            if args: fmt = fmt.format( *args )
            myclog.trace(fmt)
        except Exception as e:
            print(args)
            print(kwargs)
            raise e

    @staticmethod
    def d(fmt, *args, **kwargs):
        try:
            if 'hook' in kwargs: args = tuple(map(kwargs['hook'], args))
            if args: fmt = fmt.format( *args )
            myclog.db(fmt)
        except Exception as e:
            print(traceback.format_exc())
            print(args)
            print(kwargs)
            raise e

    @staticmethod
    def i(fmt, *args, **kwargs):
        try:
            if 'hook' in kwargs: args = tuple(map(kwargs['hook'], args))
            if args: fmt = fmt.format( *args )
            myclog.info(fmt)
        except Exception as e:
            print(traceback.format_exc())
            print(args)
            print(kwargs)
            raise e

    @staticmethod
    def w(fmt, *args, **kwargs):
        try:
            if 'hook' in kwargs: args = tuple(map(kwargs['hook'], args))
            if args: fmt = fmt.format( *args )
            myclog.warn(fmt)
        except Exception as e:
            print(traceback.format_exc())
            print(args)
            print(kwargs)
            raise e

    @staticmethod
    def e(fmt, *args, **kwargs):
        try:
            if 'hook' in kwargs: args = tuple(map(kwargs['hook'], args))
            if args: fmt = fmt.format( *args )
            myclog.error(fmt)
        except Exception as e:
            print(traceback.format_exc())
            print(args)
            print(kwargs)
            raise e

    @staticmethod
    def c(fmt, *args, **kwargs):
        try:
            if 'hook' in kwargs: args = tuple(map(kwargs['hook'], args))
            if args: fmt = fmt.format( *args )
            myclog.critical(fmt)
        except Exception as e:
            print(traceback.format_exc())
            print(args)
            print(kwargs)
            raise e

    @staticmethod
    def p(fmt, *args, **kwargs):
        try:
            if 'hook' in kwargs: args = tuple(map(kwargs['hook'], args))
            if args: fmt = fmt.format( *args )
            myclog.println(fmt)
        except Exception as e:
            print(traceback.format_exc())
            print(args)
            print(kwargs)
            raise e

log = MyLog()


if __name__ == "__main__":

    def test_MyLog():
        #from mylog.log3 import log
        log.init(header="header", directory="tmp", level="debug", max_buffer=10240, max_line=100000)
        log.i("log:info")
        log.e("log:error")
        log.w("log:warn")
        log.c("log:critical")
        log.p("log:print")
    

    def test_myclog():
        import traceback
        import time
        import sys
        try:
            print('print dir(myclog):')
            print(dir(myclog))
            e = myclog.setLogHeader("header")
            if e:
                
                print('print e:')
                print(e)
                
                print('print e.message')
                print(e.message)
            myclog.setLogDir("tmp")
            myclog.setLogMaxBuffer(10240)
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
                MyLog.e("str:%s, int:%s", "abc", 1)
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
        ./{0} test_MyLog        # 推荐用法  (输出目录 tmp/)
        ./{0} test_myclog
        """.format(__file__))
    import sys
    if len(sys.argv) == 1: Usage(), sys.exit()
    function = sys.argv[1]
    del sys.argv[1]
    eval(function)()
