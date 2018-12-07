import traceback
import time
import threading
from zutils.task.client.task_template import TaskTemplateWithFrame, TaskTemplateWithoutFrame

class WorkThread(threading.Thread):
    state = 'init'
    thread_num = 0
    thread_dict = dict()
    cur_frame = None
    def __init__(self, run_instance):
        threading.Thread.__init__(self)
        self.run_instance = run_instance
        self.thread_id = str(WorkThread.thread_num)
        WorkThread.thread_num += 1
        WorkThread.thread_dict[self.thread_id] = [self, None]
        self.run_type = None
        if isinstance(run_instance, TaskTemplateWithFrame):
            self.run_type = 'withframe'
        elif isinstance(run_instance, TaskTemplateWithoutFrame):
            self.run_type = 'withoutframe'
        else:
            raise Exception('run_instance 不是继承 TaskTemplate')


    def run(self):
        instance_frame = WorkThread.thread_dict[self.thread_id]
        while WorkThread.state == 'run':
            try:
                if self.run_type == 'withframe':
                    frame = instance_frame[1]
                    instance_frame[1] = None
                    if frame is not None:
                        self.run_instance.run(frame)
                else:
                    self.run_instance.run()

            except:
                traceback.print_exc()
                time.sleep(1)
            self.run_instance.sleep()



    @staticmethod
    def set_frame(frame):
        thread_dict = WorkThread.thread_dict
        for key in thread_dict:
            thread_dict[key][1] = frame


    @staticmethod
    def start_all():
        WorkThread.state = 'run'
        thread_dict = WorkThread.thread_dict
        for key in thread_dict:
            thread_dict[key][0].start()
            print(type(thread_dict[key][0].run_instance), 'start')
        print('start all thread')



    @staticmethod
    def stop_all():
        WorkThread.state = 'exit'
        thread_dict = WorkThread.thread_dict
        for key in thread_dict:
            thread_dict[key][0].join()
            print(type(thread_dict[key][0].run_instance), 'stop')
        print('stop all thread')




if __name__ == '__main__':
    from zutils.task.client.task_template import TaskTemplate

    class XXX(TaskTemplate):
        def sleep(self):
            print('xxxxxx')
            time.sleep(1)



    class YYY(TaskTemplate):
        def sleep(self):
            print('yyyyyy')
            time.sleep(3)

    class ZZZ(TaskTemplate):
        def run(self, frame):
            WorkThread.set_frame(frame + 1)
        def sleep(self):
            print('zzzzzz')
            time.sleep(3)



    WorkThread(XXX())
    WorkThread(YYY())
    WorkThread(ZZZ())
    WorkThread.set_frame(0)
    WorkThread.start_all()
    time.sleep(15)
    WorkThread.stop_all()


    #
    # a = {
    #     'a':1,
    #     'b':2
    # }
    #
    #
    #
    #
    #
    # v = a['a']
    # a['a'] = None
    # print(v)
    # print(a)
    #
