#!/usr/bin/env python
#coding:utf-8
import hashlib


def sha1sum(filepath, block_size=64 * 1024):
    # 与Linux命令: sha1sum 结果一致
    # result like: "665081b83216b8384f22b57d17b47633d6f43d60" -- 40个字符
    with open(filepath, 'rb') as f:
        sha1 = hashlib.sha1()
        while True:
            data = f.read(block_size)
            if not data:
                break
            sha1.update(data)
        return sha1.hexdigest() # hexdigest返回十六进制字符串, 效果 = base64.b64encode(sha1.digest()), 其中sha1.digest()返回160bit, 20Byte的二进制数据


def md5sum(filepath, block_size=64 * 1024):
    # 与Linux命令: md5sum 结果一致
    # result like: "27127a33da2d74a35fd8f9945734b813" -- 32个字符
    with open(filepath, 'rb') as f:
        _md5 = hashlib.md5()
        while True:
            data = f.read(block_size)
            if not data:
                break
            _md5.update(data)
        return _md5.hexdigest() # hexdigest返回十六进制字符串, 效果 = base64.b64encode(_md5.digest()), 其中_md5.digest()返回128bit, 16Byte的二进制数据


def md5(string):
    # result like: "27127a33da2d74a35fd8f9945734b813" -- 32个字符
    _md5 = hashlib.md5()
    _md5.update(string)
    return _md5.hexdigest() # hexdigest返回十六进制字符串, 效果 = base64.b64encode(_md5.digest()), 其中_md5.digest()返回128bit, 16Byte的二进制数据


def sha256(string):
    _sha256 = hashlib.sha256()
    _sha256.update(string)
    return _sha256.hexdigest()


if __name__ == "__main__":
    from mybase.mycksum import md5

    def test_md5():
        string = sys.argv[1]
        print md5(string)

    def test_sha256():
        string = sys.argv[1]
        print sha256(string)

    def test_sha1sum():
        file_path = sys.argv[1]
        print sha1sum(file_path)

if __name__ == "__main__":
    def Usage():
        print u"""
        python ./{0} test_md5 "forgive me."
        python ./{0} test_sha256 "forgive me."
        python ./{0} test_sha1sum ./input
        """.format(__file__)
    import sys
    if len(sys.argv) == 1: Usage(), sys.exit()
    function = sys.argv[1]
    del sys.argv[1]
    eval(function)()
