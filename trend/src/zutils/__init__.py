# from zutils.utils import *
#
# if __name__ == '__main__':
#     import numpy as np
#     c1 = TaskRedis()
#     c2 = TaskRedis('task2')
#     s1 = TaskRedis()
#     s2 = TaskRedis('task2')
#
#     c1.set_task({'a': 1, 'b': np.zeros([1,1])})
#     c2.set_task({'a': 1, 'b': np.zeros([2,2])})
#
#
#     task = s2.get_task()
#     task['c'] = task['b'].shape[0] * task['b'].shape[1]
#     s2.set_task_result(task)
#
#     task = s1.get_task()
#     task['c'] = task['b'].shape[0] * task['b'].shape[1]
#     s1.set_task_result(task)
#
#
#
#
#
#     print(c1.get_task_result())
#     print(c2.get_task_result())
