from zutils.task.task_redis import TaskRedis
from zutils.tensorflow.tf_session import TFSession
from zutils.logger import Logger
from zutils.utils import relative_project_path
import traceback
import time
import os


class TaskSingleThread:
    def __init__(self, task_name, model_class, model_config,
                 redis_host, redis_port, redis_timeout,
                 cuda, gpu_mem, allow_growth,
                 log_level, is_debug):

        cuda = str(cuda)
        self.task_name = task_name
        self.task_uname = task_name + cuda
        self.kill_last_task()
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
        self.model_class_instance = model_class(self.sess, model_config)
        self.task_run = self.model_class_instance.run



    def kill_last_task(self):
        os.makedirs(relative_project_path('logs', 'pid'), exist_ok=True)
        pid_filepath = relative_project_path(relative_project_path('logs', 'pid', self.task_uname))
        if os.path.isfile(pid_filepath):
            with open(pid_filepath) as f:
                pid = f.readline()
                if len(os.popen('ps -ef | grep %s | grep -v grep' % pid).readlines()) > 0:
                    os.system('kill -9 %s' % pid)
        with open(pid_filepath, 'w') as f:
            f.write(str(os.getpid()))

    def run(self):
        while True:
            taskid = ""
            try:
                task = self.task_redis.get_pickle_task()
                if task is None:
                    self.logger().info(self.task_uname + ' is free')
                    continue
                self.logger().info('RECV:' + task['taskId'])
                taskid = task['taskId']
                task = self.input_convert.server_convert(task)
                r = self.task_run(task)
                r = self.output_convert.server_convert(r)
                try:
                    self.logger().info('SEND:' + taskid)
                    self.task_redis.set_pickle_task_succ_result(r)

                except:
                    self.logger().error('%s' % traceback.format_exc())
                    time.sleep(5)


            except Exception as e:
                self.logger().error('%s' % traceback.format_exc())
                try:
                    self.logger().info('SEND:' + taskid)
                    self.task_redis.set_pickle_task_error_result(str(e))
                except:
                    self.logger().error('%s' % traceback.format_exc())
                    time.sleep(5)
