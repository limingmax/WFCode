from zutils.task.task_redis import TaskRedis
from zutils.logger import Logger
from zutils.utils import relative_project_path
import traceback
import time
import os
import importlib
from zutils.task.server.task_multi_template import TaskMultiTemplate
import queue
import threading


class TaskMultiThread:
    def __init__(self, max_size, thread_pool_num, redis_host, redis_port, redis_timeout, log_level, is_debug):
        self.task_dict = dict()
        self.task_queue = queue.Queue(max_size)
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_timeout = redis_timeout
        self.log_level = log_level
        self.is_debug = is_debug
        self.thread_pool_num = thread_pool_num
        self.load_task_class()

        self.kill_last_task()
    def kill_last_task(self):
        os.makedirs(relative_project_path('logs', 'pid'), exist_ok=True)
        pid_filepath = relative_project_path(relative_project_path('logs', 'pid', 'multi_task'))
        if os.path.isfile(pid_filepath):
            with open(pid_filepath) as f:
                pid = f.readline()
                if len(os.popen('ps -ef | grep %s | grep -v grep' % pid).readlines()) > 0:
                    os.system('kill -9 %s' % pid)
        with open(pid_filepath, 'w') as f:
            f.write(str(os.getpid()))


    def load_task_class(self):
        for parent, dirnames, filenames in os.walk(relative_project_path('src')):
            for filename in filenames:
                if filename.endswith('.py'):
                    with open(os.path.join(parent, filename)) as f:
                        code = f.read()
                    if ('##multi_task' in code) and ('##hahaha' not in code):
                        package_name = parent[len(relative_project_path('src/')):].replace('/', '.')

                        module_name = package_name + '.' + filename[:filename.find('.')]
                        # print(module_name)
                        try:
                            # print('name:', module_name)
                            module = importlib.import_module(module_name)
                            class_list = dir(module)
                            for class_name in class_list:

                                try:
                                    taskclass = getattr(module, class_name)

                                    if issubclass(taskclass, TaskMultiTemplate) and taskclass != TaskMultiTemplate:
                                        # print(class_name)
                                        print('add multi task:',module_name + '.' + class_name)
                                        run_instance = taskclass()
                                        self.task_dict[run_instance.task_name()] = {
                                            'run_instance': run_instance,
                                            'logger': Logger(self.log_level, run_instance.task_name(), self.is_debug),
                                            'recv_task_redis': TaskRedis(run_instance.task_name(), self.redis_host, self.redis_port, self.redis_timeout)
                                        }
                                    # print(class_name)
                                except:
                                    pass
                        except:
                            pass


    def recv_task_thread(self, task_name):
        self.task_redis = self.task_dict[task_name]['recv_task_redis']
        self.logger = self.task_dict[task_name]['logger']
        while True:
            try:
                task = self.task_redis.get_json_task()
                if task is None:
                    self.logger().info(task_name + ' is free')
                    continue
                self.logger().info('RECV:' + task['taskId'])

                while True:
                    try:
                        self.task_queue.put((task_name, task), True, 5)
                        break
                    except Exception as e:
                        self.logger().error(str(e))

                # print(self.task_queue.qsize())
            except Exception as e:
                self.logger().error('%s' % traceback.format_exc())
    def work_task_thread(self):
        task_redis = TaskRedis('taskname', self.redis_host, self.redis_port, self.redis_timeout)
        while True:
            task_id = ''
            task_name = ''
            try:
                try:
                    task_name, task = self.task_queue.get(True, 5)
                except:
                    pass
                    # self.logger().info('work thread is free')
                else:
                    task_id = task['taskId']
                    run_instance = self.task_dict[task_name]['run_instance']
                    result = run_instance.run(task_redis, task)
                    task_redis.set_task_name(task_name)
                    task_redis.set_json_task_succ_result(result, task_id)
                    self.logger().info('SEND:' + task_id)
            except Exception as e:
                self.logger().error('%s' % traceback.format_exc())
                if task_id:
                    task_redis.set_task_name(task_name)
                    task_redis.set_json_task_error_result(str(e), task_id)

    def start_recv_task_thread(self):
        recv_thread_list = list()
        for task_name in self.task_dict:
            t = threading.Thread(target=self.recv_task_thread,args=(task_name,))
            recv_thread_list.append(t)
            t.start()


    def start_work_task_thread(self):
        work_thread_list = list()

        for i in range(self.thread_pool_num):
            t = threading.Thread(target=self.work_task_thread)
            work_thread_list.append(t)
            t.start()



    def start_all(self):
        self.start_recv_task_thread()
        self.start_work_task_thread()
        while True:
            time.sleep(5)





if __name__ == '__main__':



    a = TaskMultiThread(10,10,  '127.0.0.1', 6379, 8, 'INFO', True)
    a.start_all()




    #
    #
    # for file in file_list:
    #     if file.endswith('.py') and ('fall' in file):
    #         print(file)
    #         module_name = package_name + '.' + file[:file.find('.')]
    #         print(module_name)
    #         try:
    #             module = importlib.import_module(module_name)
    #             class_list = dir(module)
    #             for class_name in class_list:
    #                 try:
    #                     if issubclass(getattr(module, class_name), TaskTemplate) and getattr(module, class_name) != TaskTemplate:
    #                         print(class_name)
    #                 except:
    #                     pass
    #         except:
    #             pass






    # module = importlib.import_module('task_client.INPUT_CONVERT_%s' % self.task_name)


    # print(x)
