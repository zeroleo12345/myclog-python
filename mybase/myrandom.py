#!/usr/bin/env python
#coding:utf-8
""" Reference:
        https://docs.python.org/2/library/random.html

random.random()函数是这个模块中最常用的方法了，它会生成一个随机的浮点数，范围是在0.0~1.0之间。
random.uniform()正好弥补了上面函数的不足，它可以设定浮点数的范围，一个是上限，一个是下限。
random.randint()随机生一个整数int类型，可以指定这个整数的范围，同样有上限和下限值，python random.randint。
random.choice(seq)可以从任何序列，比如list列表中，选取一个随机的元素返回，可以用于字符串、列表、元组等。返回:一个元素
random.shuffle()如果你想将一个序列中的元素，随机打乱的话可以用这个函数方法。
random.sample(seq, n)可以从指定的序列中，随机的截取指定长度的片断，不作原地修改。返回:列表
random.getrandbits(n) 以长整型形式返回n个随机位；
"""

import random

class MyRandom(object):
    __random_char = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789' # 62个字符
    chars = None

    @classmethod
    def randomStr(cls, length):
        return ''.join( random.choice(cls.__random_char) for _ in xrange(length) )

    @classmethod
    def randomUnicode(cls, length):
        if not cls.chars:
            common, rare = range(0x4e00, 0xa000), range(0x3400, 0x4e00)
            cls.chars = map(unichr, rare + common)
        return u''.join([random.choice(cls.chars) for _ in range(length)])

if __name__ == "__main__":
    from mybase.myrandom import MyRandom

    def test_randomstr():
        count = int(sys.argv[1])
        print MyRandom.randomStr(count)

    def test_randomUnicode():
        _unicode = MyRandom.randomUnicode(5).encode('utf8')
        print _unicode
        _utf8 = _unicode.encode('utf8')
        print _utf8
        print repr(_utf8)

if __name__ == "__main__":
    def Usage():
        print u"""
        python ./{0} test_randomstr 10
        python ./{0} test_randomUnicode
        """.format(__file__)
    import sys
    if len(sys.argv) == 1: Usage(), sys.exit()
    function = sys.argv[1]
    del sys.argv[1]
    eval(function)()
