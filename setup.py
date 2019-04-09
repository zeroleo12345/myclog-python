#!/usr/bin/env python
# coding:utf-8
import sys
from setuptools import setup, find_packages, Extension

extension_module = Extension('myclog',
                    #define_macros = [('_WIN32', '1'),],
                    include_dirs = ['myclog/myclog'],
                    sources = ['myclog/myclog/myclog.cpp', 'myclog-python/myclog-python.cpp'])

# packages = find_packages(), # 实际值为: ['mybase3']  (即py_mo_modules, 会自动查找__init__.py文件)
if sys.version_info[0] == 2:    # (2, 5, 2, 'final', 0)
    packages = ['mybase']
else:
    packages = ['mybase3']

setup(name = "myclog",
    version = "0.1",
    author = "lynatgz",
    author_email = "lyn.zhou@foxmail.com",
    description = "an Log module written in C",
    packages = packages,
    ext_modules = [extension_module],
    # zip_safe = False,
)
