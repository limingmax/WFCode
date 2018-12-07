# @Time   : 2018-9-10
# @Author : zxh
import numpy as np
class LoopQueue:
    def __init__(self, size, mean_over):
        self.data = np.zeros([size], dtype=np.float32)
        self.mean_over = mean_over
        self.index = 0
        self.size = size


    def set(self, n):
        self.data[self.index] = n
        self.index += 1
        self.index %= self.size
        return self.data.mean() >= self.mean_over


    def get(self):
        return self.data.mean() >= self.mean_over



    def clear(self):
        self.data.fill(0)





