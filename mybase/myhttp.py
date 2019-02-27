#!/usr/bin/env python.exe
#coding:utf-8
""" Referenct:
        requests:
            http://docs.python-requests.org/zh_CN/latest/api.html#requests.request
		cookielib:
			CookieJar => FileCookieJar(基类,提供接口,不提供实现) => MozillaCookieJar, LWPCookieJar
            http://blog.csdn.net/yockie/article/details/48217839
            http://www.51testing.com/html/25/349125-243929.html
            http://www.tuicool.com/articles/3YJnim/
"""

import requests
import cookielib
import urlparse
from mybase.myutil import basetype_to_str
from mybase.mylog import g_baselog
#from requests.cookies import RequestsCookieJar

class RequestFail(Exception):
    pass
class RequestError(Exception):
    """ 需退出的错误 """
    pass

class MyRequests(object):
    @staticmethod
    def get(url, params=None, **kwargs):
        return requests.get(url, params=params, **kwargs)
    @staticmethod
    def post(url, data=None, json=None, **kwargs):
        return requests.post(url, data=data, json=json, **kwargs)

class MyHttpSession(object):
    def __init__( self ):
        self.session = requests.Session()
        #self.session.headers['Accept-Language'] = 'zh-CN,zh;q=0.8'

    """
User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36
    """
    @property
    def headers( self ):
        return self.session.headers

    @property
    def proxies( self ):
        return self.session.proxies
    @proxies.setter
    def proxies( self, proxies ):
        """ proxies = { "http": "http://127.0.0.1:8888", "https": "http://127.0.0.1:8888" } """
        self.session.proxies = proxies

    @property
    def cookies( self ):
        """ return:
                RequestsCookieJar object. Subclass of cookielib.CookieJar
        """
        return self.session.cookies
    @cookies.setter
    def cookies( self, cookiejar ):
        """ params:
                cookiejar: type of cookielib.CookieJar Or ret of dict_to_cookiejar()
        """
        self.session.cookies = cookiejar
        """ HOW TO USE COOKIES:
        METHOD (1):
            ret = self.get('http://115.com')
        METHOD (2):
            ret = self.session.get('http://115.com', cookies=cookies_dict)
        """

    def save_cookies_file(self, filepath, ignore_discard=True, ignore_expires=True, type='lwp'):
        if type == 'lwp': return self._save_lwp_cookies_file( filepath, ignore_discard, ignore_expires )
        else: raise RequestError('unsupport type')

    def _save_lwp_cookies_file(self, filepath, ignore_discard=True, ignore_expires=True, type='lwp'):
            lwp_cookie_jar = cookielib.LWPCookieJar() # LWPCookieJar保存的cookies易于阅读
            requests.utils.cookiejar_from_dict( {m.name:m.value for m in self.session.cookies}, lwp_cookie_jar )
            lwp_cookie_jar.save(filepath, ignore_discard, ignore_expires)

    def load_cookies_file(self, filepath, ignore_discard=True, ignore_expires=True, type='lwp'):
        """ params:
                filepath: cookies file of Format: LWP-Cookies
                type: 'lwp' or 'json'
            return:
                cookies_dict
        """
        if type == 'lwp': self._load_lwp_cookies_file( filepath )
        elif type == 'json': return self._load_json_cookies_file( filepath )
        else: raise RequestError('unsupport type')

    def _load_lwp_cookies_file(self, filepath, ignore_discard=True, ignore_expires=True):
        """ params: cookies file of Format: LWP-Cookies
            return: cookies_dict
        """
        lwp_cookie_jar = cookielib.LWPCookieJar()
        lwp_cookie_jar.load( filepath, ignore_discard, ignore_expires )
        cookies_dict = requests.utils.dict_from_cookiejar( lwp_cookie_jar )
        return cookies_dict

    def _load_json_cookies_file(self, filepath, ignore_discard=True, ignore_expires=True):
        """ params: cookies file of Format: JSON
            return: cookies_dict
        """
        cookies_dict = {} #cookies_dict = OrderedDict()
        # read json file of cookies. (json文件不能包含注释号#)
        edit_cookies = json.load(open(filepath, 'r'))
        for cookie in edit_cookies:
            name, value = cookie['name'], cookie['value']
            cookies_dict[name]=value
        return cookies_dict

    def cookiejar_to_dict( self ):
        """ return: dict
            params:
                self.session.cookies: type of CookieJar object
        """
        return requests.utils.dict_from_cookiejar(self.session.cookies)

    def dict_to_cookiejar( self, cookies_dict, cookiejar=None, overwrite=True ):
        """ params:
                cookies_dict: result of load_cookies_file
                cookiejar: Object of MozillaCookieJar() or LWPCookieJar()
            cookiejar_from_dict() return:
                RequestsCookieJar: when cookiejar is None
                cookiejar itself: when cookiejar is MozillaCookieJar or LWPCookieJar
        """
        return requests.utils.cookiejar_from_dict( cookies_dict, cookiejar, overwrite )

    def request(self, myreq, **kwargs):
        """ params:
                myreq: class of MyRequest,
                **kwargs: SEE METHOD DEFINE: requests.Request(method=None, url=None, headers=None, files=None, data=None,
                            params=None, auth=None, cookies=None, hooks=None, json=None)
            return:
                class of requests.Response
            judge:
                if not ret.ok: print 'error code:', ret.raise_for_status()
        """
        if kwargs.has_key('Origin'): self.session.headers['Origin'] = kwargs['Origin']
        if kwargs.has_key('Referer'): self.session.headers['Referer'] = kwargs['Referer']
        if kwargs.has_key('X_Requested_With'): self.session.headers['X-Requested-With'] = kwargs['X_Requested_With']
        response = self.session.request( method=myreq.method, url=myreq.url, params=myreq.params, data=myreq.data, files=myreq.files, headers=myreq.headers )
        return response

    def get(self, url, params=None, **kwargs):
        """ requests.get(url, params=None, **kwargs)
                params – (optional) Dictionary or bytes to be sent in the query string for the Request
            judge:
                if not ret.ok: print 'error code:', ret.raise_for_status()
        """
        if (kwargs.has_key('proxies') and kwargs['proxies']) or self.session.proxies:
            verify = False
        else:
            verify = True
        response = self.session.get(url, params=params, verify=verify, **kwargs)
        return response

    def post(self, url, data=None, json=None, **kwargs):
        """ requests.post(url, data=None, json=None, **kwargs)
                data – (optional) Dictionary, bytes, or file-like object to send in the body of the Request
                json – (optional) json data to send in the body of the Request
            judge:
                if not ret.ok: print 'error code:', ret.raise_for_status()
        """
        if (kwargs.has_key('proxies') and kwargs['proxies']) or self.session.proxies:
            verify = False
        else:
            verify = True
        response = self.session.post(url, data=data, json=json, verify=verify, **kwargs)
        return response

    @staticmethod
    def response_to_myjson( response, encoding=str ):
        """ params:
                response: result of request(), get(), post()
            return: MyJsonResponse
        """
        json_dict = response.json()
        return MyJsonResponse( json_dict, encoding )

class MyRequest(object):
    def __init__(self, url, method='GET', params=None, data=None, files=None, headers=None, mylog=g_baselog):
        self.url = url
        self.method = method
        self.params = params
        self.data = data
        self.files = files
        self.headers = headers
        self.mylog = mylog
        self._debug()

    def _debug(self):
        if self.mylog.level == self.mylog.TRACE:
            try:
                func = inspect.stack()[2][3] # 获取上一层函数名
            except NameError:
                import inspect
                func = inspect.stack()[2][3]
            msg = "CLASS:%s FUNC:%s URL:%s METHOD:%s PARAMS:%s DATA:%s" %\
                (self.__class__.__name__, func, self.url, self.method, self.params, self.data)
            self.mylog.trace(msg)

class MyJsonResponse(dict):
    def __init__(self, json_dict, encoding=str, mylog=g_baselog):
        if encoding is str:
            json_dict = basetype_to_str( json_dict )
        self.update( json_dict )
        self.encoding = encoding
        self.mylog = mylog
        self._debug()

    def _debug(self):
        if self.mylog.level == self.mylog.TRACE:
            try:
                func = inspect.stack()[2][3] # 获取上一层函数名
            except NameError:
                import inspect
                func = inspect.stack()[2][3]
            msg = "CLASS:%s FUNC:%s CONTENT:%s" % (self.__class__.__name__, func, self)
            self.mylog.trace(msg)

    def find(self, item='', all=False, start=0, **kwargs):
        """
        not find return `None`
        find
            when all=True, return `list`
            when all=False, return `dict`
        """
        if type(item) is not self.encoding:
            raise Exception( 'self encoding:%s, params encoding:%s' % (self.encoding, type(item)) )
        if isinstance(self[item], list):
            return self.find_list(item, all, start, **kwargs)
        elif isinstance(self[item], dict):
            return self.find_dict(item, all, **kwargs)

    def find_list(self, item='', all=False, start=0, **kwargs):
        try:
            ret = None
            key, value = kwargs.popitem()
            for d in self[item][start:]:
                if not d.has_key(key): continue
                if d[key] != value: continue
                if all:
                    ret = [].append(d)
                else:
                    ret = d
                    break
            if ret is None:
                pdb.set_trace()
                self.mylog.error( "Response:%s find None" % self )
                raise Exception('Response find None.item:%s,key:%s,value%s' % (item, key, value) )
            return ret
        except Exception as e:
            self.mylog.error( "%s" % traceback.format_exc() )
            raise e

    def find_dict(self, item='', all=False, **kwargs):
        try:
            ret = None
            key, value = kwargs.popitem()
            for d in self[item]:
                if not d.has_key(key): continue
                if d[key] != value: continue
                if all:
                    ret = [].append(d)
                else:
                    ret = d
                    break
            if ret is None:
                self.mylog.error( "Response:%s" % self )
                raise Exception('Response find None.item:%s,key:%s,value' % (item, key, value) )
            return ret
        except Exception as e:
            self.mylog.error( "%s" % traceback.format_exc() )
            raise e

def url_encode(string, coding='utf8'):
    """ return: str
    example:
        命中注定.Only.You.2015.HD720P.X264.torrent  ==>  %C3%FC%D6%D0%D7%A2%B6%A8.Only.You.2015.HD720P.X264.torrent
    """
    if isinstance(string, unicode): string = string.encode( coding )
    return requests.utils.quote(string)

def url_decode(string, coding='utf8'):
    """ return: str
    example:
        %C3%FC%D6%D0%D7%A2%B6%A8.Only.You.2015.HD720P.X264.torrent ==> 命中注定.Only.You.2015.HD720P.X264.torrent

        python2:        https://docs.python.org/2/library/urllib.html
            from urllib import unquote
            unquote('/%7Econnolly/')

        python3:        https://docs.python.org/3/library/urllib.parse.html
            from urllib.parse import urlparse
            urlparse('http://www.cwi.nl:80/%7Eguido/Python.html')
    """
    if isinstance(string, unicode): string = string.encode( coding )
    return requests.utils.unquote(string)

def url_query(url, key, pos=0):
    """ return:
            success: str, auto decode string like: %3A%2F%2F. it is char of '://'
                     None, when not find
    params:
        url: full url address
        key: params name
        pos: choose the position of the same params name
    Reference:
        https://docs.python.org/2/library/urlparse.html
    """
    parse_result = urlparse.urlparse( url )
    _dict = urlparse.parse_qs( parse_result.query, keep_blank_values=True )
    if _dict.has_key(key):
        return _dict[key][pos]
    else:
        return None

if __name__ == "__main__":

    from mybase.myhttp import MyHttpSession
    g_http_session = MyHttpSession()
    _user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36'
    g_http_session.headers['User-Agent'] = _user_agent

    def test_get():
        url = 'http://passport.115.com/?ct=open_login&t=renren'
        params = { 'ct': 'open_login', 't': 'renren', }
        ret = g_http_session.get(url, params=params)
        print dir(g_http_session.session)
        if not ret.ok: # ret.status_code == 200
            print 'request fail!'
            return False
        print ret.text
        ## Translate to Json when you need
        #myjson = MyHttpSession.response_to_myjson( ret )

    def test_post():
        url = 'https://graph.renren.com/oauth/grant'
        data = { 'login_type':'false', 'username':'username' }
        ret = g_http_session.post(url, data=data)
        if not ret.ok: # ret.status_code == 200
            print 'request fail!'
            return False
        print ret.text
        ## Translate to Json when you need
        #myjson = MyHttpSession.response_to_myjson( ret )

    def test_request():
        url = 'http://115.com/lixian/'
        params = {'ct': 'lixian', 'ac': 'add_task_url'}
        data = { 'url': url, 'uid': 123, }   
        myreq = MyRequest(method='POST', url=url, params=params, data=data) #myreq = MyRequest(method='GET', url=url, params=params)
        ret = g_http_session.request(myreq)
        if not ret.ok: # ret.status_code == 200
            print 'request fail!'
            return False
        print ret.text
        ## Translate to Json when you need
        #myjson = MyHttpSession.response_to_myjson( ret )

    def test_cookie():
        filepath = os.path.join( os.getcwd(), 'wxweb_cookie.txt')
        # GET
        test_get()
        # SAVE
        g_http_session.save_cookies_file(filepath=filepath, type='lwp')

        # LOAD
        _cookies_dict = g_http_session.load_cookies_file(filepath=filepath, type='lwp')
        g_http_session.cookies = g_http_session.dict_to_cookiejar( _cookies_dict )
        # GET
        test_get()

    def test_url_decode():
        s = """ %C3%FC%D6%D0%D7%A2%B6%A8.Only.You.2015.HD720P.X264.torrent """
        print url_decode(s)

    def test_urlparse():
        from myhttp import url_query
        url = 'https://detail.tmall.com/item.htm?id=537834393438&ali_trackid=2:mm_118228572_16886088_62146954:1476252375_2k2_152035812&pvid=10_120.236.175.102_5063_1476181659852'
        key = 'id'
        value = url_query( url, key=key, pos=0 )
        print 'url:{}\n    key:{}\n    value:{}\n'.format(url, key, value)

        url = 'https://s.click.taobao.com/t_js?tu=https%3A%2F%2Fs.click.taobao.com%2Ft%3Fe%3Dm%253D2%2526s%253Di%252FImp2iDchQcQipKwQzePOeEDrYVVa64LKpWJ%252Bin0XLjf2vlNIV67uo6qebPsnJfJhSgLssdd1aG1SGOCoeQQ3OkYVv%252FBIeYVrQCiuvnd2SNRtwQ8bCX3%252F7rUu9Y23qq8v5XPGCNToEWWF7eYJ6Jg24YopDbQ9JtomfkDJRs%252BhU%253D%26pvid%3D50_111.15.44.151_27190_1480233571226%26ref%3D%26et%3Dt9TvIUdx1T1yFesas6%252Fu%252ByAkdyNpMlGV'
        key = 'tu'
        value = url_query( url, key=key, pos=0 )
        print 'url:{}\n    key:{}\n    value:{}\n'.format(url, key, value)
        """
        1. urlparse.urlparse:
                ParseResult(scheme='https', netloc='detail.tmall.com', path='/item.htm', params='',
                    query='id=537834393438&ali_trackid=2:mm_118228572_16886088_62146954:1476252375_2k2_152035812&pvid=10_120.236.175.102_5063_1476181659852', fragment='')
        1. urlparse.parse_qs:
                dict: {'pvid': ['10_120.236.175.102_5063_1476181659852'], 'ali_trackid': ['2:mm_118228572_16886088_62146954:1476252375_2k2_152035812'], 'id': ['537834393438']}
        """

if __name__ == "__main__":
    def Usage():
        print u"""
        python ./{0} test_get
        python ./{0} test_urlparse
        """.format(__file__)
    import sys, os, pdb 
    if len(sys.argv) == 1: Usage(), sys.exit()
    function = sys.argv[1]
    del sys.argv[1]
    eval(function)()
