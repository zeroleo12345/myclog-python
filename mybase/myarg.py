#!/usr/bin/python
#coding:utf-8
""" Reference:
        argparse:
            https://docs.python.org/2/library/argparse.html
        optparse: 
            optparse was officially deprecated after Python 2.7
"""
from __future__  import print_function
import sys


# for k,v in args._get_kwargs():
# 调用方法: parser.print_help()
def init_args():
    import argparse
    parser = argparse.ArgumentParser(description='%s' % (sys.argv[0]))
    parser.add_argument('--topic', action='append', metavar='<FILE>', type=str, help='radius dictionary file', required=True)
    # 指定参数-h的回调函数: parser.print_help = Usage  # Usage为函数对象
    return parser.parse_args()

    # Example:
    """ 参数: True or False. -d                     """
    #parser.add_argument('-d', action='store_true', help='turn on debug flag', default=False, dest="isDebug")
    """ 参数: 数字. -p 6379                """
    #parser.add_argument('-p', '--port', metavar='<PORT>, type=int, help='http server port listen, default: 80')
    """ 参数: 单个字符串. -c myconf.conf   """
    #parser.add_argument('-c', metavar='<FILE>', type=str, help='config file path', required=False, dest='conf')
    """ 参数: 多个字符串. -dict /dir/dict1 -dict /dir/dict2 """ # nargs=1 指定参数后跟几个参数, 可不使用此参数
    #parser.add_argument('-dict', action='append', metavar='<FILE>', type=str, help='radius dictionary file', required=True)


if __name__ == '__main__':
    args = init_args()
    print(args)
