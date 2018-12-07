# @Time   : 2018-9-10
# @Author : zxh
import hashlib
import os

def cal_md5(filepath):
    md5file=open(filepath, 'rb')
    md5=hashlib.md5(md5file.read()).hexdigest()
    md5file.close()
    return md5

def write_md5(filepath, md5):
    with open(filepath, 'w') as f:
        f.write(md5)


def read_md5(filepath):
    if not os.path.isfile(filepath):
        return ''
    with open(filepath, 'r') as f:
        return f.read(32)


def remove_file(filepath):
    if os.path.isfile(filepath):
        os.remove(filepath)

__all__ = ['cal_md5', 'write_md5', 'read_md5', 'remove_file']