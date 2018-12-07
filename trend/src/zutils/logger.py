# @Time   : 2018-9-10
# @Author : zxh
import logging
from zutils.utils import relative_project_path
import os
class Logger:
    CRITICAL = 'CRITICAL'
    ERROR = 'ERROR'
    WARNING = 'WARNING'
    INFO = 'INFO'
    DEBUG = 'DEBUG'
    NOTSET = 'NOTSET'
    def __init__(self, level, filename, is_debug):
        self.kill_last_task(filename)
        formatter = logging.Formatter("%(asctime)s - %(filename)s[%(lineno)d] - %(levelname)s: %(message)s")
        self.logger = logging.getLogger()
        self.logger.setLevel(getattr(logging, level))
        os.makedirs(relative_project_path('logs'), exist_ok=True)
        logfile = relative_project_path('logs', filename +".log")
        fh = logging.FileHandler(logfile, mode='a')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        if is_debug:
            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)


    def kill_last_task(self, filename):
        os.makedirs(relative_project_path('logs', 'pid'), exist_ok=True)
        pid_filepath = relative_project_path(relative_project_path('logs', 'pid', filename))
        if os.path.isfile(pid_filepath):
            with open(pid_filepath) as f:
                pid = f.readline()
                if len(os.popen('ps -ef | grep %s | grep -v grep' % pid).readlines()) > 0:
                    os.system('kill -9 %s' % pid)
        with open(pid_filepath, 'w') as f:
            f.write(str(os.getpid()))


    def __call__(self):
        return self.logger

