#!/usr/bin/env python
#coding:utf-8

class Singleton(type): # __metaclass__
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
"""
def singleton(cls): # µ¥ÀýÐÞÊÎÆ÷
    instances={}
    def getinstance(*args,**kw):
        if cls not in instances.keys():
            instances[cls]=cls(*args,**kw)
        return instances[cls]
    return getinstance
"""

if __name__ == "__main__":
    def Usage():
        print """
        ./mysingleton.py
        """
    import sys, os, pdb
    if len(sys.argv) == 1: Usage(), sys.exit()
    function = sys.argv[1]
    del sys.argv[1]
    eval(function)()
