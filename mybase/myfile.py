#!/usr/bin/python
#coding:utf-8

class MyFile(object):
    def __init__(self, filename, flag='wb'):
        self._file = open(filename, flag)

    def write(self, byte):
        self._file.write(byte)
    def read(self, byte):
        return self._file.read()

if __name__ == "__main__":
    def test_write_to_file():
        myfile = MyFile('./output.tmp')
        byte = 'fefe'
        myfile.write(byte)

if __name__ == "__main__":
    def Usage():
        print """
        ./myfile.py test_write_to_file
        """
    import sys, os, pdb
    if len(sys.argv)==1: Usage(), sys.exit()
    function = sys.argv[1]
    del sys.argv[1]
    eval(function)()
