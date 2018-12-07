# @Time   : 2018-9-10
# @Author : zxh
import time
class Frequency:
    def __init__(self, duration, frequency, max_len = 100):
        self.queue = list()
        self.duration = duration
        self.frequency = frequency
        self.max_len = max_len

    def add_one(self):
        cur_time = time.time()
        while len(self.queue) > 0 and (cur_time - self.queue[0] > self.duration):
            self.queue.pop(0)
        self.queue.append(cur_time)
        while (len(self.queue) > self.max_len):
            self.queue.pop(0)
        return len(self.queue) >= self.frequency

