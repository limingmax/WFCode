# @Time   : 2018-10-24
# @Author : zxh
from zutils.zrpc.zmq.redismq import RedisMQ
import traceback
import time
import threading

def init_args(*args, **kwargs):
    def create(cls):
        def wrap():
            return cls(*args, **kwargs)
        return wrap
    return create


def map_handle(url, handle_name, max_queue_size):
    def create(cls):
        def wrap():
            instance = cls()
            if not hasattr(instance, 'map_url_func_size_dict'):
                instance.map_url_func_size_dict = dict()
            if not hasattr(instance, 'map_url_list'):
                instance.map_url_list = list()

            func = getattr(instance, handle_name)
            instance.map_url_func_size_dict[url] = (func, max_queue_size)
            instance.map_url_list.append(url)
            instance.map = lambda url: instance.map_url_func_size_dict[url]

            return instance
        return wrap
    return create


class ThreadpoolServer:
    def __init__(self, register_address, server_cls_list, logger, protocol, recv_timeout, send_timeout, thread_num=1):
        self.server_instance_list = server_cls_list
        self.logger = logger
        self.protocol = protocol
        self.thread_num = thread_num
        self.register_address = register_address
        self.task_names = list()
        self.max_queue_list = list()
        self.server_cls_list = server_cls_list
        self.init_mutex = threading.Lock()
        self.recv_timeout = recv_timeout
        self.send_timeout = send_timeout


    def work_thread(self):
        requests_map = dict()
        task_names = list()
        max_queue_list = list()
        for server_cls in self.server_cls_list:
            cls = server_cls()
            for url in cls.map_url_list:
                if requests_map.get(url) is not None:
                    raise Exception('taskname ' + url + ' is not only')
                func, max_size= cls.map(url)
                requests_map[url] = func
                task_names.append(url)
                max_queue_list.append(max_size)

        if self.init_mutex.acquire():
            if len(self.task_names) == 0:
                self.task_names = task_names
                self.max_queue_list = max_queue_list
            self.init_mutex.release()

        rmq = RedisMQ(self.register_address, self.send_timeout, self.recv_timeout)
        task_names_str = str(task_names)
        while True:
            try:
                request = rmq.pop(task_names, self.protocol, False)
                if request is None:
                    self.logger().info(str(threading.currentThread().ident) + ' ' + task_names_str + ' free')
                    continue
                self.logger().info('RECV:' + request.taskid)
                try:
                    result = requests_map[request.task_name](request.task)
                    request.response_succ(result)
                    self.logger().info('SEND:' + request.taskid)
                except Exception as e:
                    self.logger().error('%s' % traceback.format_exc())
                    request.response_error(str(e))
                    self.logger().info('SENDERROR:' + request.taskid)

            except:
                self.logger().error('%s' % traceback.format_exc())
                time.sleep(1)

    def heartbeat_thread(self):
        rmq = RedisMQ(self.register_address, 30, 30)

        while True:
            try:
                task_names = list()
                max_queue_list = list()
                if self.init_mutex.acquire():
                    task_names = self.task_names
                    max_queue_list = self.max_queue_list
                    self.init_mutex.release()

                for task_name, max_size in zip(task_names, max_queue_list):
                    rmq.set_queue_maxsize(task_name, max_size, 15)
            except:
                self.logger().error('%s' % traceback.format_exc())
                time.sleep(1)

            time.sleep(5)

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




