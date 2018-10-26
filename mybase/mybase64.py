#!/usr/bin/env python
#coding:utf-8

""" Reference:
    https://docs.python.org/2/library/base64.html
    http://www.cnblogs.com/Security-Darren/p/3853054.html
"""

# 1. b64encode(s, altchars=None)
# 2. b64decode(s, altchars=None)
# 3. standard_b64encode(s)
# 4. standard_b64decode(s)
# 5. urlsafe_b64encode(s)
# 6. urlsafe_b64decode(s)
# 方法3的 base64.standard_b64encode(s) 和 方法4的 base64.standard_b64decode(s) 等价于 方法1的 base64.b64encode(s, None) 和 方法2的 base64.b64decode(s, None)
# 方法5的 base64.urlsafe_b64encode(s) 和 方法6的 base64.urlsafe_b64decode(s) 等价于 方法1的 base64.b64encode(s , '-_') 和 方法2的 base64.b64decode(s , '-_')
# 即在编/解码过程中使用'-'和'_'替代标准Base64字符集中的'+'和'/', 生成可以在URL中使用的Base64格式文本
# alterchars 使用例子:
# >>> print base64.b64encode('i\xb7\x1d\xfb\xef\xff', '-_') 
# 12 abcd--__ 

import base64

def Usage():
    print u"""
    python ./{0}
    """.format(os.path.basename(__file__))

if __name__ == "__main__":
    import sys, os
    if len(sys.argv) == 1: Usage(), exit()
    function = sys.argv[1]
    del sys.argv[1]
    eval(function)()
