import hashlib


def md5(s):
    __md5 = hashlib.md5()
    __md5.update(str(s))
    return __md5.hexdigest()
