import redis
import pickle
import json
from redis.exceptions import ResponseError
import os
import importlib
import zutils.task.data_convert
from zutils.convert import convert_dict
from zutils.utils import relative_project_path
class TaskRedis:
    def __init__(self, task_name='task', host='127.0.0.1', port=6379, timeout=8):
        self.timeout = timeout
        self.redis_conn = redis.Redis(host=host, port=port)
        self.set_task_name(task_name)

    def set_task_name(self, task_name):
        self.task_name = task_name
        self.task_list_name = 'AISVR_' + self.task_name
        self.task_incr_id_key = 'INCRID_' + self.task_list_name
        self.task_result_pre = 'TASK_' + self.task_incr_id_key + '_'
        self.cur_taskid = None


    # 命名规则InputConvert OutputConvert
    def create_data_convert(self):
        os.makedirs(relative_project_path('src', 'task_client'), exist_ok=True)
        if os.path.isfile(relative_project_path('src', 'task_client', '__init__.py')):
            os.mknod(relative_project_path('src', 'task_client', '__init__.py'))

        code = self.redis_conn.get('INPUT_CONVERT_' + self.task_name)
        if code is None:
            print('input convert is None, use default.')
            input_convert_class = zutils.task.data_convert.DefaultConvert
        else:
            with open(relative_project_path('src', 'task_client',
                                            'INPUT_CONVERT_%s.py' % self.task_name), 'wb') as f:
                f.write(code)

            module = importlib.import_module('task_client.INPUT_CONVERT_%s'% self.task_name)
            # os.remove(relative_project_path('src', 'task_client', 'INPUT_CONVERT_%s.py' % self.task_name))
            input_convert_class = getattr(module, 'InputConvert')


        code = self.redis_conn.get('OUTPUT_CONVERT_' + self.task_name)
        if code is None:
            output_convert_class = zutils.task.data_convert.DefaultConvert
            print('output convert is None, use default.')
        else:
            with open(relative_project_path('src', 'task_client',
                                            'OUTPUT_CONVERT_%s.py' % self.task_name), 'wb') as f:
                f.write(code)

            module = importlib.import_module('task_client.OUTPUT_CONVERT_%s'% self.task_name)
            # os.remove(relative_project_path('src', 'task_client', 'OUTPUT_CONVERT_%s.py' % self.task_name))

            output_convert_class = getattr(module, 'OutputConvert')

        return input_convert_class, output_convert_class

    def upload_data_convert(self, task_class):
        module_name = task_class.__module__
        package_list = module_name.split('.')
        # path = relative_project_path('src', *package_list[:len(package_list) - 1])
        input_convert_path = relative_project_path('src', *package_list[:len(package_list) - 1], 'input_convert.py')
        output_convert_path = relative_project_path('src', *package_list[:len(package_list) - 1], 'output_convert.py')

        if os.path.isfile(input_convert_path):
            with open(input_convert_path) as f:
                code = f.read()
                self.redis_conn.set('INPUT_CONVERT_' + self.task_name, code)
        else:
            print('input convert is None, use default.')

        if os.path.isfile(output_convert_path):
            with open(output_convert_path) as f:
                code = f.read()
                self.redis_conn.set('OUTPUT_CONVERT_' + self.task_name, code)
        else:
            print('output convert is None, use default.')



    def create_taskid(self):
        try:
            return self.task_result_pre + str(self.redis_conn.incr(self.task_incr_id_key))
        except ResponseError as e:
            print(e)
            self.redis_conn.delete(self.task_incr_id_key)
            return self.task_result_pre + str(self.redis_conn.incr(self.task_incr_id_key))

    def set_pickle_task(self, data_obj, task_name=None):
        if task_name is not None:
            self.set_task_name(task_name)
        self.cur_taskid = self.create_taskid()
        data_obj['taskId'] = self.cur_taskid
        data = pickle.dumps(data_obj)
        self.redis_conn.lpush(self.task_list_name, data)
        self.redis_conn.expire(self.task_list_name, self.timeout)
        return self.cur_taskid

    def set_json_task(self, data_obj, task_name=None):
        if task_name is not None:
            self.set_task_name(task_name)
        self.cur_taskid = self.create_taskid()
        data_obj['taskId'] = self.cur_taskid
        data = json.dumps(data_obj)
        self.redis_conn.lpush(self.task_list_name, data)
        self.redis_conn.expire(self.task_list_name, self.timeout)
        return self.cur_taskid


    def get_pickle_task(self):
        data = self.redis_conn.brpop(self.task_list_name, self.timeout)
        if data is not None:
            r = pickle.loads(data[1])
            self.cur_taskid = r['taskId']
            return r
        return None

    def get_json_task(self):
        data = self.redis_conn.brpop(self.task_list_name, self.timeout)
        if data is not None:
            r = json.loads(data[1])
            self.cur_taskid = r['taskId']
            return r
        return None


    def set_pickle_task_succ_result(self, result, taskid=None):
        if taskid is None:
            taskid = self.cur_taskid

        r = {
            'code': 0,
            'data': result,
            'errorInfo': ""
        }
        self.redis_conn.lpush(taskid , pickle.dumps(r))
        self.redis_conn.expire(taskid, self.timeout)


    def set_json_task_succ_result(self, result, taskid=None):
        if taskid is None:
            taskid = self.cur_taskid

        r = {
            'code': 0,
            'data': result,
            'errorInfo': ""
        }
        convert_dict(r)
        self.redis_conn.lpush(taskid , json.dumps(r))
        self.redis_conn.expire(taskid, self.timeout)


    def set_pickle_task_error_result(self, errorInfo, taskid=None):
        if taskid is None:
            taskid = self.cur_taskid
        r = {
            'code': 1,
            'errorInfo': errorInfo
        }
        self.redis_conn.lpush(taskid , pickle.dumps(r))
        self.redis_conn.expire(taskid, self.timeout)


    def set_json_task_error_result(self, errorInfo, taskid=None):
        if taskid is None:
            taskid = self.cur_taskid

        r = {
            'code': 1,
            'errorInfo': errorInfo
        }
        self.redis_conn.lpush(taskid , json.dumps(r))
        self.redis_conn.expire(taskid, self.timeout)

    def get_pickle_task_result(self, taskid=None):
        if taskid is None:
            taskid = self.cur_taskid
        data = self.redis_conn.brpop(taskid, self.timeout)
        if data is not None:
            r = pickle.loads(data[1])
            if r['code'] != 0:
                raise Exception(r['errorInfo'])
            return r['data']
        return None

    def get_json_task_result(self, taskid=None):
        if taskid is None:
            taskid = self.cur_taskid
        data = self.redis_conn.brpop(taskid, self.timeout)
        if data is not None:
            r = json.loads(data[1])
            if r['code'] != 0:
                raise Exception(r['errorInfo'])
            return r['data']
        return None

if __name__ == '__main__':
    xx = TaskRedis('facedetect', '192.168.200.50')
    a = xx.get_json_task()
    xx.set_json_task_succ_result({'abc': 'asd'})
    print(a)