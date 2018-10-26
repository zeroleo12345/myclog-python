#!/usr/bin/python
#coding:utf-8

import sys
def get_this_filename():
    """ example: 'myutil.py' """
    argv0 = sys.argv[0].split("/");
    return argv0[ len(argv0)-1 ];

def set_encoding(encoding='utf-8'):
    """ multiprocessing should call this function in def(): """
    if sys.getdefaultencoding() != encoding:
        reload(sys)
        sys.setdefaultencoding(encoding)

# os.path.join( path, *paths )
# os.path.exists( filepath )

import collections
def basetype_to_str(data):
    """ 全数据类型 ==> str.(编码由 unicode ==> utf8) """
    if isinstance(data, unicode):
        return data.encode('utf8')
    elif isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(basetype_to_str, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(basetype_to_str, data))
    else:
        return data

import inspect
import re
import sys
def myprint(*args):
    # Traceback(filename='./test_inspect.py', lineno=22, function='<module>', code_context=['myprint(spam, 1)\n'], index=0)
    filename = inspect.getframeinfo(inspect.currentframe().f_back)[0]
    lineno = inspect.getframeinfo(inspect.currentframe().f_back)[1]
    code_context = inspect.getframeinfo(inspect.currentframe().f_back)[3]
    #
    pmsg = 'Filename: {}, Line: {}'.format(filename, lineno)
    for line in code_context:
        # print line
        regex = '{}\((.*)\)'.format( sys._getframe().f_code.co_name )
        m = re.search(regex, line)
        if m is None:
            return
        arg_names =  m.group(1)
        arg_name_list = arg_names.split(', ')
        for pos, arg_name in enumerate(arg_name_list):
            pmsg = pmsg + ', {} = {}'.format(arg_name, args[pos])
    print pmsg

from itertools import islice
def dict_chunks(data, size=10000):
    """ 字典分批. (yield 相当于非阻塞的返回)
    param:
        data: type of dict
    """
    total_size = len(data)
    if total_size <= size:
        yield data
        return
    it = iter(data)
    for i in xrange(0, total_size, size):
        yield {k:data[k] for k in islice(it, size)}

def list_chunks(data, size=10000):
    """ 列表分批. (yield 相当于非阻塞返回)
    param:
        data: type of list
    """
    total_size = len(data)
    if total_size <= size:
        yield data
        return
    for i in range(0, total_size, size):
        yield data[i:i+size]


if __name__ == '__main__':
    def test_list_chunks():
        from mybase.myutil import list_chunks
        data = range(0, 100)
        for d in list_chunks(data, 100):
            print d

    def test_dict_chunks():
        from mybase.myutil import dict_chunks
        data = {i:i for i in range(0, 100)}
        for d in dict_chunks(data, 100):
            print d

    def test_myprint():
        from mybase.myutil import myprint
        spam = 42
        myprint(spam, 1)

    def test_set_encoding():
        from mybase.myutil import set_encoding; set_encoding('utf-8')

    def test_basetype_to_str():
        from mybase.myutil import basetype_to_str
        #data = { u'spam':u'eggs', u'foo':frozenset([u'Gah!']), u'bar':{ u'baz': 97 }, u'list':[u'list', (True, u'Maybe'), set([u'and', u'a', u'set', 1])]}
        data = {u'code': u'', u'uid': 38097705, u'cur': 0, u'is_asc': 0, u'page_size': 115, u'r_all': 0, u'state': True, u'scid': u'', u'snap': u'', u'type': 0, u'is_q': 0, u'star': 0, u'errNo': 0, u'error': u'', u'is_share': 0, u'offset': 0, u'path': [{u'aid': 1, u'pid': 0, u'name': u'\u6587\u4ef6', u'cid': 0}], u'data': [{u'e': u'', u'cid': u'355757364261129015', u'cc': u'', u'm': 1, u'pid': u'0', u'fc': 0, u'p': 0, u'n': u'\u6211\u7684\u63a5\u6536', u'pc': u'fd79zrkarbx9n65fhd', u'sh': u'0', u'u': u'', u't': u'1412425582', u'aid': u'1', u'ns': u'\u6211\u7684\u63a5\u6536', u'hdf': 1}], u'count': 0, u'data_source': u'MYSQL', u'cid': 0, u'natsort': 1, u'limit': 115, u't': 0.010831117630005, u'stdir': 0, u'aid': 1, u'order': u'user_ptime'}
        print basetype_to_str(data)
        print 'original:', data

if __name__ == '__main__':
    def Usage():
        print """ 
        python {0} test_list_chunks
        python {0} test_dict_chunks
        python {0} test_myprint
        python {0} test_basetype_to_str
        """.format(__file__)
    if len(sys.argv)==1: Usage(), sys.exit()
    function = sys.argv[1]
    del sys.argv[1]
    eval(function)()
