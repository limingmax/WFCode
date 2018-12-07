# @Time   : 2018-10-24
# @Author : zxh
from zutils.zrpc.zmq.redismq import RedisMQ
import traceback
import time
import threading
class AbstractServer:
    # def handle1(self, task):
    #     return {'key':'value'}

    def requests_map(self):
        return {
            'handle1': {
                'func': 'xxx',
                'max': 10
            }
        }

class ThreadpoolServer:
    def __init__(self, register_address, server_instance_list, logger, protocol, thread_num=1):
        self.server_instance_list = server_instance_list
        self.logger = logger
        self.requests_map = dict()
        self.protocol = protocol
        self.thread_num = thread_num
        self.register_address = register_address
        self.task_names = list()
        self.max_queue_list = list()

        for server_instance in server_instance_list:
            name_func_dict = server_instance.requests_map()
            for task_name in name_func_dict:
                if self.requests_map.get(task_name) is not None:
                    raise Exception('task_name ' + task_name + ' is not only')
                self.requests_map[task_name] = name_func_dict[task_name]['func']
                self.task_names.append(task_name)
                self.max_queue_list.append(name_func_dict[task_name]['max'])

    def work_thread(self):
        rmq = RedisMQ(self.register_address, 30)
        while True:
            try:
                request = rmq.pop(self.task_names, self.protocol, False)
                if request is None:
                    self.logger().info('free')
                    continue
                try:
                    result = self.requests_map[request.task_name](request.task)
                    request.response_succ(result)
                except Exception as e:
                    request.response_error(str(e))

            except:
                self.logger().error('%s' % traceback.format_exc())
                time.sleep(1)

    def heartbeat_thread(self):
        rmq = RedisMQ(self.register_address, 30)

        while True:
            try:
                for task_name, max_size in zip(self.task_names, self.max_queue_list):
                    rmq.set_queue_maxsize(task_name, max_size, 30)
            except:
                self.logger().error('%s' % traceback.format_exc())
                time.sleep(1)


            time.sleep(15)

    def start(self):
        heartbeat = threading.Thread(target=self.heartbeat_thread)
        heartbeat.start()
        if self.thread_num == 1:
            self.work_thread()
        else:
            work_thread_list = list()
            for i in range(self.thread_num):
                t = threading.Thread(target=self.work_thread)
                work_thread_list.append(t)
                t.start()

        while True:
            time.sleep(5)




