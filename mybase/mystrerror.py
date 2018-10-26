#!/usr/bin/env python
#coding:utf-8

if __name__ == "__main__":
    def Usage():
        print u"""
        python {0}
        """.format(__file__)
    import sys
    if len(sys.argv) == 1: Usage(), sys.exit()
    function = sys.argv[1]
    del sys.argv[1]
    eval(function)()
