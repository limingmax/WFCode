import redis
import pickle
import json
from zutils.convert import convert_dict
import traceback

def check_protocol(protocol):
    if protocol != 'JSON' and protocol != 'PICKLE':
        raise Exception('protocol ' + protocol + ' is not exist')

class AbstractTask:
    def __init__(self, redis_conn, timeout, taskid, task_name, task, protocol):
        check_protocol(protocol)
        self.redis_conn = redis_conn
        self.timeout = timeout
        self.taskid = taskid
        self.task_name = task_name
        self.task = task
        self.protocol = protocol


class Response(AbstractTask):

    def get(self):
        data = self.redis_conn.brpop(self.taskid, self.timeout)
        if data is not None:
            raise Exception('ResultGetter pop timeout')
        if self.protocol == 'JSON':
            r = json.loads(data[1])
        else:
            r = pickle.loads(data[1])

        if r['code'] != 0:
            raise Exception(r['errorInfo'])
        return r['data']


class Request(AbstractTask):

    def response_succ(self, result):
        r = {
            'code': 0,
            'data': result,
            'errorInfo': ""
        }
        if self.protocol == 'JSON':
            convert_dict(r)
            r = json.dumps(r)
        else:
            r = pickle.dumps(r)
        self.redis_conn.lpush(self.taskid , r)
        self.redis_conn.expire(self.taskid, self.timeout)


    def response_error(self, errorInfo):
        r = {
            'code': 1,
            'errorInfo': errorInfo
        }
        if self.protocol == 'JSON':
            r = json.dumps(r)
        else:
            r = pickle.dumps(r)
        self.redis_conn.lpush(self.taskid, r)
        self.redis_conn.expire(self.taskid, self.timeout)


class RedisMQ:
    def __init__(self, register_address, timeout):
        self.register_address = register_address
        self.address_instance_dict = dict()
        self.interface_address_dict = dict()
        index = register_address.find(':')
        if index == -1:
            raise Exception('error register_address')
        host = register_address[:index]
        port = int(register_address[index + 1:])
        self._timeout = timeout
        self._conn = redis.Redis(host=host, port=port)

    def get_redis_conn(self, task_name):
        return self._conn, self._timeout

    def key_task_list(self, task_name):
        return 'AISVR_' + task_name

    def key_task_list_to_task_name(self, key_task_list):
        return key_task_list[6:].decode("utf-8")

    def create_taskid(self, task_name):
        key_task_incr_id = 'INCRID_' + self.key_task_list(task_name)
        task_result_pre = 'TASK_' + key_task_incr_id + '_'
        try:
            redis_conn, _ = self.get_redis_conn(task_name)

            return task_result_pre + str(redis_conn.incr(key_task_incr_id))
        except:
            traceback.print_exc()
            redis_conn, _ = self.get_redis_conn(task_name)
            redis_conn.delete(key_task_incr_id)
            return task_result_pre + str(redis_conn.incr(key_task_incr_id))

    def set_queue_maxsize(self, task_name, max_size, timeout):
        limit_key = 'LIMIT_' + self.key_task_list(task_name)
        redis_conn, _ = self.get_redis_conn(task_name)
        if timeout == 0:
            redis_conn.set(limit_key, str(max_size))
        else:
            redis_conn.setex(limit_key, str(max_size), timeout)

    def push(self, task_name, request, protocol='PICKLE'):
        check_protocol(protocol)
        redis_conn, timeout = self.get_redis_conn(task_name)
        taskid = self.create_taskid(task_name)
        request['taskId'] = taskid

        if protocol == 'JSON':
            data = json.dumps(request)
        else:
            data = pickle.dumps(request)

        redis_conn.lpush(self.key_task_list(task_name), data)
        redis_conn.expire(self.key_task_list(task_name), timeout)

        return Response(redis_conn, timeout, taskid, task_name, request, protocol)

    def pop(self, task_names, protocol='PICKLE', is_throw_except=True):
        check_protocol(protocol)

        if isinstance(task_names, str):
            task_names = [task_names]
        else:
            task_names = list(task_names)

        task_list_names = list()

        for task_name in task_names:
            task_list_names.append(self.key_task_list(task_name))

        redis_conn, timeout = self.get_redis_conn(task_names[0])

        data = redis_conn.brpop(task_list_names, timeout)
        if data is None:
            if is_throw_except:
                raise Exception('redismq pop timeout')
            else:
                return None

        task_name = self.key_task_list_to_task_name(data[0])
        if protocol == 'JSON':
            task = json.loads(data[1])
        else:
            task = pickle.loads(data[1])

        return Request(redis_conn, timeout, task['taskId'], task_name, task, protocol)







if __name__ == '__main__':
    register_address = '192.168.213.51:6379'
    rmq = RedisMQ(register_address, 30)
    response = rmq.push('/testabc', {'a': 'b'}, protocol='JSON')
    response = rmq.push('/testabcd', {'a': 'b'}, protocol='JSON')

    # rmq.set_queue_maxsize('/testabc', 10, 60)


    request = rmq.pop(['/testabc','/testabcd'], protocol='JSON')
    print(request.task_name, request.task)
    request = rmq.pop(['/testabc', '/testabcd'], protocol='JSON')
    print(request.task_name, request.task)

    # result_set.response_succ({'aa': 'bb'})


# if __name__ == '__main__':
#     register_address = '192.168.213.51:6379'
#     rmq = RedisMQ(register_address, 30)
#
#     rmq.set_queue_maxsize('/testabc', 10, 60)
#
#
#     request = rmq.pop('/testabc', protocol='JSON')
#     print(request.task_name, request.task)
#
#
#     request.response_succ({'aa': 'bb'})

