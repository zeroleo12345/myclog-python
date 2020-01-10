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

1. 用法
Pycrypto用法:    参考:  http://blog.csdn.net/yyhustim/article/details/8539065
    from Crypto.Cipher import DES3
    obj = DES3.new('abcdefgh', DES3.MODE_ECB)
    plain = 'text'
    # 加密
    encrypt = obj.encrypt( plain )
    # 机密
    plain = obj.decrypt( encrypt )

M2Crypto用法:
    from M2Crypto.EVP import Cipher

2. 安装
Windows x64版本:
    wget https://pypi.python.org/pypi/M2CryptoWin64/0.21.1-3
    jieya M2CryptoWin64-0.21.1-3.tar.gz; cd M2CryptoWin64-0.21.1-3;
    pip install --egg M2CryptoWin64
"""
try:
    from M2Crypto.EVP import Cipher
except ImportError as e:
    print """
    MISS module! Please excute: pip install M2Crypto
        MAC:
            sudo env LDFLAGS="-L$(brew --prefix openssl)/lib" \
            CFLAGS="-I$(brew --prefix openssl)/include" \
            SWIG_FEATURES="-cpperraswarn -includeall -I$(brew --prefix openssl)/include" \
            pip install m2crypto
    """
    raise e
import base64

def encrypt_3des(key, text, usebase64=False):
    cipher = Cipher(alg='des_ede3_ecb', key=key, op=1, iv='\0'*16)
    s = cipher.update(text)
    if usebase64:
        return base64.b64encode( s + cipher.final() )
    else:
        return s + cipher.final()

def decrypt_3des(key, text, usebase64=False):
    if usebase64:
        text = base64.b64decode( text )
    cipher = Cipher(alg='des_ede3_ecb', key=key, op=0, iv='\0'*16)
    s = cipher.update(text)
    return s + cipher.final()

def _autofill(key):
    if len(key) > 16:
        return key[:16]
    elif len(key) < 16:
        return key + '0'*(16-len(key))
    else:
        return key

def encrypt_aes(key, text, iv='\0'*16, usebase64=False):
    """ aes比3des: 加解密速度快, 资源消耗低, 安全级别高
    param:
        key: 密钥, 16个字符
        note: 当key或iv不足16个字符的时候, 后面补字符'0'; 当超过16个字符的时候, 截断为前面16个字符
        note: 标准Base64编码会出现字符+和/，在URL中不能作为参数，而urlsafe的base64编码，其实是把字符+和/分别变成-和_
    """
    key = _autofill(key) # 当使用 aes_256时候, key需要32个字符; 而使用aes_128时, key需要16个字符
    iv = _autofill(iv)
    cipher = Cipher(alg='aes_128_cbc', key=key, op=1, iv=iv) # aes_256_cbc, aes_256_ecb
    s = cipher.update(text)
    _enc = s + cipher.final()
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
    cipher = Cipher(alg='aes_128_cbc', key=key, op=0, iv=iv) # aes_256_cbc, aes_256_ecb
    s = cipher.update(text)
    return s + cipher.final()

def read( filepath ):
    with open(filepath, 'r') as f:
        text = f.read() #读取整个文件，字符串显示
        return text

def write( filepath, byte ):
    with open(filepath, 'wb') as f:
        f.write( byte )

if __name__ == "__main__":
    def test_create():
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

        args = init_args()
        key = read( args.key_file )
        text = read( args.input_file )
    
        if args.is_decrypt:
            plaintext = decrypt_3des(key, text)
            print plaintext
            if args.output_file is not None: write( args.output_file, plaintext )
        else:
            encrypt_text = encrypt_3des(key, text)
            print encrypt_text.encode('hex')
            if args.output_file is not None: write( args.output_file, encrypt_text )

    def test_3des():
        from mybase.myencrypt import encrypt_3des, decrypt_3des
        print '3des'
        jdata = {'data': 'R8wQ/2HFbOBqtCDjJrIyRMIE/y4larbGQKJUZOLO9Lzjzc7yCuYM+A==', 'time': '1492518984.96'}
        key = jdata['time']
        text = jdata['data']
        print "key:%s, len:%s, text:%s" % ( key, len(key), text )
        encrypt_text = encrypt_3des(key, text)
        print "encrypt_text:%s, len:%s" % ( encrypt_text.encode('hex'), len(encrypt_text) )
        plaintext = decrypt_3des(key, encrypt_text)
        print "plaintext:%s" % (plaintext)

        print '\n######### test ##########'
        key = key
        text = text
        print "key:%s, len:%s, text:%s" % ( key, len(key), text )
        encrypt_text = encrypt_3des(key, text, True)
        print "encrypt_text:%s, len:%s" % ( encrypt_text.encode('hex'), len(encrypt_text) )
        plaintext = decrypt_3des(key, encrypt_text, True)
        print "plaintext:%s" % (plaintext)

    def test_aes():
        from mybase.myencrypt import encrypt_aes, decrypt_aes

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

    def test_aes_decrypt_base64():
        def init_args():
            import argparse
            parser = argparse.ArgumentParser()
            parser.add_argument('-d', action='store_true', help='for decrypt', required=False, default=True, dest='is_decrypt')
            parser.add_argument('-k', metavar='key', type=str, help='key', required=True, dest='key')
            parser.add_argument('-iv', metavar='iv', type=str, help='iv', required=True, dest='iv')
            parser.add_argument('-text', metavar='text', type=str, help='text', required=True, dest="text")
            return parser.parse_args()

        args = init_args()
        if args.is_decrypt:
            decrypt_data = decrypt_aes(args.key, args.text, iv=args.iv, usebase64=True)
            print decrypt_data

if __name__ == "__main__":
    def Usage():
        print u"""
        python {0} test_create -k key_file -i text_file -o encrypt_file
        python {0} test_create -k key_file -i encrypt_file -o text_file -d
        python {0} test_3des
        python {0} test_aes_decrypt_base64 -k "K6BUP6kcGQ" -iv 'xiaobaizhushou' -text "uHxAALnr7N4aqW6r7mGaZaGYjRtnEES40dFXhr44daOl2Ig57AdyCM_R-avcYuuk"
        python {0} test_aes
        python {0} test_aes_decrypt_from_java
        """.format(__file__)
    import sys
    if len(sys.argv) == 1: Usage(), sys.exit()
    function = sys.argv[1]
    del sys.argv[1]
    eval(function)()
