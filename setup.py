#!/usr/bin/env python
# coding:utf-8
from setuptools import setup, find_packages, Extension

extension_module = Extension('myclog',
                    #define_macros = [('_WIN32', '1'),],
                    include_dirs = ['myclog/myclog'],
                    sources = ['myclog/myclog/myclog.cpp', 'myclog-python/myclog-python.cpp'])

setup(name = "myclog",
    version = "0.1",
    author = "lynatgz",
    author_email = "zeroleo12345@163.com",
    description = "an Log module written in C",
    packages = find_packages(), # 即py_mo_modules, 会自动查找__init__.py文件
    ext_modules = [extension_module],
)
