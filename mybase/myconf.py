#!/usr/bin/env python.exe
#coding:utf-8
 
""" Reference:
    第三方模块, python2.6 - 3.5通用
        https://docs.python.org/3/library/configparser.html
"""

try:
    from configparser import SafeConfigParser
except Exception as e:
    print """
    need module: pip install configparser
    """
    raise e
import os

# 构造函数: configparser.ConfigParser(defaults=None, dict_type=collections.OrderedDict, allow_no_value=False, delimiters=('=', ':'), comment_prefixes=('#', ';'), inline_comment_prefixes=None, strict=True, empty_lines_in_values=True, default_section=configparser.DEFAULTSECT, interpolation=BasicInterpolation(), converters={})
class MyConf(SafeConfigParser):
    def __init__(self, conf_path=None):
        """ raise: Exception when config file not exist """
        SafeConfigParser.__init__(self, allow_no_value=True, inline_comment_prefixes='#') # SafeConfigParser继承ConfigParser
        if conf_path:
            if not os.path.exists(conf_path):
                raise Exception('conf file: %s not exist' % conf_path)
            self.read(conf_path)

    def write(self, filepath):
        with open( filepath, "w" ) as f:
            SafeConfigParser.write(self, f)
    # has_section(section)
    # has_option(section, option)

    def dump(self):
        for section, item in self.iteritems():
            print 'section:{}'.format(section)
            for key, value in item.iteritems():
                print '    key:{}, value:{}'.format(key, value)

if __name__ == "__main__":
    """ 配置文件模板: test_read.conf
[COMMON]
g_server_ip = 127.0.0.1 # 行内注释
cq_dir=E:\mywork\cqair  ## key 必须小写! 因为ConfigParser会自动转成小写
chrome_dir = E:\cygwin64\home\zlx\code\baicai\demo\chrome41.0.2272.89_x86_downg
test = 0

[COLLECTION1]
image = \[CQ:image,file=[\w.]*\]
coupon = ((http|https)://){0,1}shop.m.taobao.com/shop/coupon.htm[\w\?=&amp;]+
click = ((http|https)://){0,1}s.click.taobao.com/[0-9a-zA-Z]+
    """
    def test_init_conf():
        try:
            conf_path = 'test_read.conf'
            myconf = MyConf(conf_path)
        except Exception as e:
            print 'conf file: %s not exist' % conf_path
            return False
        for section, item in myconf.iteritems():
            print "section:{}".format(section)
            for key, value in item.iteritems():
                print "    key:{}, value:{}".format(key, value)
        # print '    conf:', myconf.items()
        filepath = 'test_write.conf'
        myconf.write( filepath )
        return True

    def test_new_conf():
        config = MyConf()
        config['DEFAULT'] = {'ServerAliveInterval': '45', 'Compression': 'yes'}
        config.write( 'test_write.conf' )


if __name__ == "__main__":
    def Usage():
        print u"""
        python ./{0} test_init_conf
        """.format(__file__)
    import sys 
    if len(sys.argv) == 1: Usage(), sys.exit()
    function = sys.argv[1]
    del sys.argv[1]
    eval(function)()
