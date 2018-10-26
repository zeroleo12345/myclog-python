#!/usr/bin/env python.exe
#coding:utf-8
"""
三种算法: DES, 3DES, AES.  越往后越建议使用

0. 区别
加解密的三个库: M2Crypto, Pycrypto, pyDes.
        pip install cryptography    # 2017年新库, 目标是python标准加密库
        pip install M2Crypto
        pip install Pycrypto
        pip install pyDes

跨平台建议使用Pycrypto, 但是效率上不如C库的M2Crypto. 而pyDes效率最慢.
"""

''' Reference:
        https://blog.csdn.net/dawn_statdust/article/details/54893362
'''

try:
    from cryptography.hazmat.primitives import padding
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
except ImportError as e:
    print """
    MISS module! Please excute: pip install cryptography
    """
    raise e

import base64

backend = default_backend()

def _autofill(key):
    if len(key) > 16:
        return key[:16]
    elif len(key) < 16:
        return key + '0'*(16-len(key))
    else:
        return key

def pkcs7_padding(data):
    if not isinstance(data, bytes):
        raise Exception('need type: bytes')

    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()
    return padded_data

def pkcs7_unpadding(padded_data):
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    data = unpadder.update(padded_data)
    try:
        uppadded_data = data + unpadder.finalize()
    except ValueError:
        raise Exception('无效的加密信息!')

    return uppadded_data

def encrypt_aes(key, text, iv='\0'*16, usebase64=False):
    """ aes比3des: 加解密速度快, 资源消耗低, 安全级别高 param: key: 密钥, 16个字符
            note: 当key或iv不足16个字符的时候, 后面补字符'0'; 当超过16个字符的时候, 截断为前面16个字符
            note: 标准Base64编码会出现字符+和/，在URL中不能作为参数，而urlsafe的base64编码，其实是把字符+和/分别变成-和_
        text: b''   // Byte类型
    """
    # 该模块采用如下定义：
    #   加解密算法为AES，密钥位长128，CBC模式，填充标准PKCS7  (有其他类型如: aes_256_cbc, aes_256_ecb)
    #   签名算法为SHA256的HMAC，密钥位长128位
    #   密钥可以设置过期时间
    key = _autofill(key) # 当使用 aes_256时候, key需要32个字符; 而使用aes_128时, key需要16个字符
    iv = _autofill(iv)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()
    text = pkcs7_padding(text)
    s = encryptor.update(text)
    _enc = s + encryptor.finalize()
    if usebase64:
        return base64.urlsafe_b64encode( _enc )
    else:
        return _enc

def decrypt_aes(key, text, iv='\0'*16, usebase64=False):
    """ aes比3des: 加解密速度快, 资源消耗低, 安全级别高
    param:
        key: 密钥, 16个字符
        note: 当key或iv不足16个字符的时候, 后面补字符'0'; 当超过16个字符的时候, 截断为前面16个字符
        note: 标准Base64编码会出现字符+和/，在URL中不能作为参数，而urlsafe的base64编码，其实是把字符+和/分别变成-和_
    """
    key = _autofill(key) # 当使用 aes_256时候, key需要32个字符; 而使用aes_128时, key需要16个字符
    iv = _autofill(iv)
    if usebase64:
        text = base64.urlsafe_b64decode( text )

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    return pkcs7_unpadding(decryptor.update(text))

def read( filepath ):
    with open(filepath, 'r') as f:
        text = f.read() #读取整个文件，字符串显示
        return text

def write( filepath, byte ):
    with open(filepath, 'wb') as f:
        f.write( byte )

if __name__ == "__main__":
    def init_args():
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('-d', action='store_true', help='for decrypt', required=False, default=False, dest='is_decrypt')
        parser.add_argument('-k', metavar='<key_file>', type=str, help='key file', required=True, dest='key_file')
        parser.add_argument('-i', metavar='<input_file>', type=str, help='input file(text)', required=True, dest="input_file")
        parser.add_argument('-o', metavar='<output_file>', type=str, help='output file(encrypt)', required=False, dest="output_file")
        #print dir(parser)
        #parser.print_help()
        return parser.parse_args()

    def test_aes():
        from mybase.myencrypt2 import encrypt_aes, decrypt_aes

        print 'aes'
        # 加密
        data = "3e4b9a13857e53aa9cbf9e0e9fe38b01"
        key = "HDEBCSTPQN"
        # iv = "robot_wxid"
        iv = '\0' * 16
        usebase64 = True
        print 'data: {}'.format( data )
        print 'key: {}'.format( key )
        print 'iv: {}'.format( iv )
        print 'usebase64: {}'.format( usebase64 )
        encrypt_text = encrypt_aes(key, data, iv=iv, usebase64=usebase64)
        print "encrypt_text:%s" % (encrypt_text)

        # 解密
        # print '\n######### test ##########'
        # key = key
        # text = text
        # print "key:{}, len:{}".format( key, len(key) )
        # print 'text:{}'.format( text )
        # encrypt_text = encrypt_aes(key, text, usebase64=True)
        # print "encrypt_text:%s, len:%s" % ( encrypt_text.encode('hex'), len(encrypt_text) )
        # plaintext = decrypt_aes(key, encrypt_text, usebase64=True)
        # print "plaintext:%s" % (plaintext)

    def test_aes_decrypt_from_java():
        import binascii
        # 加密
        data = "com/tencent/mm/pluginsdk/ui/chat/ChatFooter$2"
        key = "password"
        iv = "robot_wxid"
        # iv = '\0' * 16
        usebase64 = False
        print 'data: {}, len:{}'.format( data, len(data) )
        print 'key: {}, len:{}'.format( key, len(key) )
        print 'iv: {}, len:{}'.format( iv, len(iv) )
        print 'usebase64:{}'.format( usebase64 )
        encrypt_data = encrypt_aes(key, data, iv=iv, usebase64=usebase64)
        hex_encrypt_data = ( binascii.b2a_hex( encrypt_data ) )
        print "hex encrypt data: %s, len:%s" % ( hex_encrypt_data, len(hex_encrypt_data) )
        b64_encrypt_data = base64.urlsafe_b64encode( encrypt_data )
        print "b64 encrypt data: %s, len:%s" % (b64_encrypt_data, len(b64_encrypt_data))

        # 解密
        decrypt_data = decrypt_aes(key, b64_encrypt_data, iv=iv, usebase64=True)
        print "decrypt data: %s" % (decrypt_data)

if __name__ == "__main__":
    def Usage():
        print u"""
        python ./{0} test_create -k key_file -i text_file -o encrypt_file
        python ./{0} test_create -k key_file -i encrypt_file -o text_file -d
        python ./{0} test_aes
        python ./{0} test_aes_decrypt_from_java
        """.format(__file__)
    import sys
    if len(sys.argv) == 1: Usage(), sys.exit()
    function = sys.argv[1]
    del sys.argv[1]
    eval(function)()
