# coding:utf-8
class ILog(object):
    @staticmethod
    def print_hook(msg):
        return repr(msg).decode('string_escape')
