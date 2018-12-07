# @Time   : 2018-9-10
# @Author : zxh
import numpy as np
from zutils.utils import wrapper_mutex

class OneCopy:
    def __init__(self):
        self.data = None
        wrapper_mutex(self, self.set)
        wrapper_mutex(self, self.get)

    def set(self, data):
        self.data = np.copy(data)

    def get(self):
        ret = None
        if self.data is not None:
            ret = self.data
            self.data = None
        return ret


class One:
    def __init__(self):
        self.data = None
        wrapper_mutex(self, self.set)
        wrapper_mutex(self, self.get)

    def set(self, data):
        self.data = data

    def get(self):
        ret = None
        if self.data is not None:
            ret = self.data
            self.data = None
        return ret