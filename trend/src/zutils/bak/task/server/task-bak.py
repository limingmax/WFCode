from zutils.task.task_redis import TaskRedis
from zutils.tensorflow.tf_session import TFSession
from zutils.convert import convert_dict,convert_dict_log
from zutils.logger import Logger
from zutils.utils import relative_project_path
import traceback
import time
import json
import os

class Task:
    def __init__(self, task_name, model_class, model_config,
                 redis_host, redis_port, redis_timeout,
                 cuda, gpu_mem, allow_growth,
                 log_level, is_debug):

        cuda = str(cuda)
        self.task_name = task_name
        self.task_uname = task_name + cuda
        self.task_redis = TaskRedis(task_name, redis_host, redis_port, redis_timeout)
        self.task_redis.upload_data_convert(model_class)
        self.input_convert, self.output_convert = self.task_redis.create_data_convert()
        self.input_convert = self.input_convert()
        self.output_convert = self.output_convert()

        if cuda is not None:
            self.sess = TFSession(cuda, gpu_mem, allow_growth).get_sess()
        else:
            self.sess = None
        self.logger = Logger(log_level, self.task_uname, is_debug)
        self.model_class_instance = model_class(self.sess, self.task_redis,model_config)
        self.task_run = self.model_class_instance.run
        self.kill_last_task()


    def kill_last_task(self):
        os.makedirs(relative_project_path('logs', 'pid'), exist_ok=True)
        pid_filepath = relative_project_path(relative_project_path('logs', 'pid', self.task_uname))
        if os.path.isfile(pid_filepath):
            with open(pid_filepath) as f:
                pid = f.readline()
                if len(os.popen('ps -ef | grep %s | grep src | grep -v grep' % pid).readlines()) > 0:
                    os.system('kill -9 %s' % pid)
        with open(pid_filepath, 'w') as f:
            f.write(str(os.getpid()))


    def get_task(self, get_func):
        try:
            task = get_func()
            if task is None:
                self.logger().info(self.task_uname + ' is free')
                return None
            self.logger().info('RECV: ' + task['taskId'])
            task = self.input_convert.server_convert(task)
            return task
        except:
            self.logger().error('%s' % traceback.format_exc())
            time.sleep(5)
        return None


    def set_task_result(self, set_func, result):
        try:
            result = self.output_convert.server_convert(result)
            if 'json' in getattr(set_func, '__name__'):
                convert_dict(result)
            r = {
                'code': 0,
                'data': result,
                'errorInfo': ""
            }

        except Exception as e:
            self.logger().error('%s' % traceback.format_exc())
            r = {
                'code': 1,
                'errorInfo': str(e)
            }

        try:
            set_func(r)
            self.logger().info('SEND:', result['taskId'])
        except:
            self.logger().error('%s' % traceback.format_exc())
            time.sleep(5)

    def run(self):
        pass


class B(Task):
    def xxx(self):
        print('xx')

