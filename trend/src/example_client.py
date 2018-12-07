# @Time   : 2018-10-24
# @Author : zxh


# 测试
import requests


r = requests.get('http://192.168.213.51:8899/test1')

print(r.json())

r = requests.post('http://192.168.213.51:8899/test1', json={'key': 1})

print(r.json())