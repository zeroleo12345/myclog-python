import os
import time
import logging
from mybase.mysingleton import Singleton

""" Reference:
        api:
            https://docs.python.org/2/library/logging.html
            https://docs.python.org/2/library/logging.handlers.html
        src:
            https://hg.python.org/cpython/file/2.7/Lib/logging/__init__.py
        example:
            http://www.jb51.net/article/42626.htm
            http://www.cnblogs.com/dkblog/archive/2011/08/26/2155018.html
        datetime格式:
            http://www.cnblogs.com/codemo/archive/2012/04/18/PythonTime.html
"""

class BaseLog(object):
    CLOSE = 0                       # 0
    TRACE = 1                       # 1
    DEBUG = logging.DEBUG           # 10
    INFO = logging.INFO             # 20
    WARN = logging.WARN             # 30
    ERROR = logging.ERROR           # 40
    CRITICAL = logging.CRITICAL     # 50
    def __init__(self): pass
    def close(self): pass
    def info(self, msg): pass
    def error(self, msg): pass
    def warn(self, msg): pass
    def db(self, msg): pass
    def trace(self, msg): pass
    @property
    def level(self): return self.CLOSE

class MyFormatter(logging.Formatter):
    def format(self, record):
        msg = logging.Formatter.format(self, record)
        if isinstance(msg, str):
            msg = msg.decode('utf8', 'replace')
        return msg

class MyLog(BaseLog):
    __metaclass__ = Singleton # 单例

    @property
    def filename(self):
        # %prefix_%yyyymmdd_%pid.log
        if not self._filename:
            if not self.log_dir: raise Exception('log_dir is None')
            yyyymmdd = time.strftime("%Y%m%d", time.localtime() )
            self._filename = os.path.join( self.log_dir, self.prefix + '_' + yyyymmdd + '_' + str(os.getpid()) + '.log' )
        return self._filename
    @property
    def tmp_filename(self):
        # %prefix_%yyyymmdd_%pid.log.tmp
        return self.filename + '.tmp'
    @property
    def level(self):
        """ return: number """
        return self.logger.getEffectiveLevel()
    @level.setter
    def level(self, _level):
        self.logger.setLevel( _level )

    """ function:
            for log to term, can set the termlevel.
            for log to file, can set the filelevel and log_dir.
    """
    def __init__(self, name='default'):
        self.name = name
        self.logger = logging.getLogger(self.name) # if no name is specified, return root logger of the hierarchy

    def init(self, filelevel="CLOSE", termlevel="CLOSE", log_dir='./', prefix='', mode='a'):
        if not prefix: raise Exception('prefix is None')
        self._filename = None
        self.log_dir = log_dir
        self.prefix = prefix
        self.mode = mode

        self.set_format()
        self.add_filelog(filelevel)
        self.add_termlog(termlevel)
        self.level = self.DEBUG  # 总日志级别默认为: DEBUG

    def set_format(self):
        #logging.Formatter.converter = time.gmtime # 设置输出时间为GMT格林威治时间
        self.fmt = "%(asctime)s [%(levelname)s] %(message)s" # [%(filename)s:%(lineno)d]
        self.datefmt = "%Y-%m-%d %H:%M:%S"

    def add_filelog(self, level):
        """ 1. File Log """
        self.filelevel = eval( 'self.%s' % level.upper() )
        if not self.filelevel: return
        #print('FileLog:%s, Level:%s' % ( self.tmp_filename, level ))
        _handler = logging.FileHandler( filename=self.tmp_filename, mode=self.mode, encoding='utf-8' )
        _formatter = MyFormatter( fmt=self.fmt, datefmt=self.datefmt )
        _handler.setFormatter( _formatter )
        _handler.setLevel( self.filelevel )
        self.logger.addHandler( _handler )
        return _handler.stream.fileno()

    def add_termlog(self, level):
        """ 2. Term Log """
        self.termlevel = eval( 'self.%s' % level.upper() )
        #print(self.termlevel)
        if not self.termlevel: return
        #print('TermLog, Level:%s' % level)
        _handler = logging.StreamHandler( stream=None )
        _formatter = logging.Formatter( fmt=self.fmt, datefmt=self.datefmt )
        _handler.setFormatter( _formatter )
        _handler.setLevel( self.termlevel )
        self.logger.addHandler( _handler )
        """ logging.basicConfig( level = logging.DEBUG, datefmt = '%Y-%m-%d %H:%M:%S', filename = logfile, filemode = 'w',) """

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)
    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)
    def warn(self, msg, *args, **kwargs):
        # same as: logger.warning
        self.logger.warn(msg, *args, **kwargs)
    def db(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)
    def trace(self, msg, *args, **kwargs): # more debug info
        if self.filelevel == self.TRACE or self.termlevel == self.TRACE:
            self.logger.debug(msg, *args, **kwargs)

    def close(self):
        for handler in self.logger.handlers:
            #print(handler.stream.fileno())
            handler.close()
            self.logger.removeHandler(handler)
        #logging.shutdown()
        if os.path.exists(self.tmp_filename): os.rename(self.tmp_filename, self.filename)

""" GLOBAL """
g_baselog = BaseLog()

if __name__ == '__main__':
    """ HOW TO USE Singleton """
    from mybase.mylog import MyLog
    log = MyLog()
    log.init( log_dir='./', prefix='logtest' )
    log.level = log.DEBUG  # 设置总日志级别
    # fileno = log.add_filelog( 'DEBUG' ) or log.add_termlog( 'DEBUG' )

    def test_log_to_file():
        try:
            fileno = log.add_filelog( 'DEBUG' ) # 增加文件日志, 且设置子日志级别
            print(fileno)   # Always is 3 in Windows
            #time.sleep(10000)
            log.info('中文支持:info')
            log.error('log:error')
            log.warn('log:warn')
            log.db('log:debug')
        except:
            import traceback
            print(traceback.format_exc())
        finally:
            log.close()

    def test_log_to_term():
        try:
            log.add_termlog( 'DEBUG' ) # 增加终端日志, 且设置子日志级别
            log.info(u'中文支持:info')
            log.error('log:error')
            log.warn('log:warn')
            log.db('log:debug')
        except:
            import traceback
            print(traceback.format_exc())
        finally:
            log.close()

if __name__ == "__main__":
    def Usage():
        print(""" 
        python ./mylog.py test_log_to_file
        python ./mylog.py test_log_to_term
        """)
    import sys, os, pdb 
    if len(sys.argv) == 1: Usage(), sys.exit()
    function = sys.argv[1]
    del sys.argv[1]
    eval(function)()
