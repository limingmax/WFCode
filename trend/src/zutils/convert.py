# @Time   : 2018-9-10
# @Author : zxh
from scipy import misc
from PIL import Image
import io
import base64
import re
import numpy as np

def arr_to_pngbase64(img, h=None, w=None, is_filp=False):
    if h is not None:
        if ((img.shape[0] != h) or (img.shape[1] != w)):
            img = misc.imresize(img, (h, w))
    img = Image.fromarray(img.astype('uint8'))
    if is_filp:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    output_buffer = io.BytesIO()
    img.save(output_buffer, format='png')
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data).decode()
    # print(len(base64_str))
    return "data:image/png;base64," + base64_str



def arr_to_jpgbase64(img, h=None, w=None, is_filp=False):
    if h is not None:
        if ((img.shape[0] != h) or (img.shape[1] != w)):
            img = misc.imresize(img, (h, w))
    img = Image.fromarray(img.astype('uint8'))
    if is_filp:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    output_buffer = io.BytesIO()
    img.save(output_buffer, format='jpg')
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data).decode()
    # print(len(base64_str))
    return "data:image/jpg;base64," + base64_str




def base64_to_arr(b64):
    base64_data = re.sub('^data:image/.+;base64,', '', b64)
    byte_data = base64.b64decode(base64_data)
    image_data = io.BytesIO(byte_data)
    img = Image.open(image_data)
    return np.array(img)


def convert_list(l):
    if len(l) == 0:
        return
    type_val = type(l[0])
    type_str = str(type_val)
    n = len(l)
    if type_val == str:
        pass
    elif 'int' in type_str:
        if type_val != int:
            for i in range(n): l[i] = int(l[i])
    elif 'float' in type_str:
        if type_val != float:
            for i in range(n): l[i] = int(l[i])
        for i in range(n): l[i] = round(l[i], 6)
    elif type_val == dict:
        for i in range(n): convert_dict(l[i])
    elif 'array' in type_str:
        for i in range(n): l[i] = l[i].tolist()
        for i in range(n): convert_list(l[i])
    elif type_val == list:
        for i in range(n): convert_list(l[i])
    else:
        raise Exception('convert_list no ' + type_str)


def convert_dict(d):
    for k, v in d.items():
        type_val = type(v)
        type_str = str(type_val)
        if type_val == str:
            pass
        elif 'int' in type_str:
            if type_val != int:
                d[k] = int(v)
        elif 'float' in type_str:
            if type_val != float:
                v = float(v)
            d[k] = round(v, 6)

        elif type_val == dict:
            convert_dict(v)
        elif 'array' in type_str:
            v = v.tolist()
            d[k] = v
            convert_list(v)
        elif type_val == list:
            convert_list(v)
        else:
            raise Exception('convert_dict no ' + type_str)


def convert_list_log(l):
    ret = list()
    n = len(l)
    if n == 0:
        return ret
    type_val = type(l[0])
    if type_val == str:
        for i in range(n):
            lenv = len(l[i])
            if lenv > 20:
                ret.append('<char[%d]>' % lenv)
            else:
                ret.append(l[i])
    elif type_val == list:
        for i in range(n):
            lenv = len(l[i])
            if lenv > 20:
                type_str = str(type(l[i][0]))
                ret.append('<%s[%d]>' % (type_str[type_str.find("'") + 1: -2], lenv))


            else:
                ret.append(convert_list_log(l[i]))
    elif type_val == dict:
        for i in range(n):
            ret.append(convert_dict_log(l[i]))
    else:
        for i in range(n):
            ret.append(l[i])
    return ret


def convert_dict_log(d):
    ret = dict()
    for k, v in d.items():
        type_val = type(v)
        if type_val == str:
            lenv = len(v)
            if lenv > 20:
                ret[k] = '<char[%d]>' % lenv
            else:
                ret[k] = v
        elif type_val == list:
            lenv = len(v)
            if lenv > 20:
                type_str = str(type(v[0]))
                ret[k] = '<%s[%d]>' % (type_str[type_str.find("'")+1: -2], lenv)
            else:
                ret[k] = convert_list_log(v)
        elif type_val == dict:
            ret[k] = convert_dict_log(v)
        else:
            ret[k] = v
    return ret


__all__ = ['arr_to_pngbase64', 'arr_to_jpgbase64', 'base64_to_arr', 'convert_list', 'convert_dict', 'convert_list_log', 'convert_dict_log']




# x = {
#     'a':1,
#     'b':[2]* 100,
#     'c':[[3]* 200, [4]* 300 ],
#     'd': 'c' * 123,
#     'e': [1.1] * 345,
#     'f':[]
# }
#
# import json
# print(str(int))
# t = convert_dict_log(x)
# print(json.dumps(t))