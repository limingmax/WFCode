# @Time   : 2018-9-10
# @Author : zxh
import cv2
from zutils.utils import wrapper_mutex
import threading
import traceback
import time
class VideoCapture:
    def  __init__(self, device=None, is_background=False, background_sleep_time =0.01, with_frame_num=False, is_to_rgb=False):
        self.device = None
        cap = None
        if device is None:
            for i in range(8):
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    self.device = i
                    break
        else:
            cap = cv2.VideoCapture(device)
            if cap.isOpened():
                self.device = device

        if self.device is None:
            raise Exception('cap is not opened')

        self.is_to_rgb = is_to_rgb
        ret, frame = cap.read()

        if (not ret) or (frame is None):
            raise Exception('cap read error')
        self.height = frame.shape[0]
        self.width = frame.shape[1]
        cap.release()
        self.cap = None
        wrapper_mutex(self, self.read_one)
        self.with_frame_num = with_frame_num

        self.is_background = is_background
        self.background_sleep_time = background_sleep_time
        self.frame = None
        self.frame_num = 0

        self.is_run = False

        if self.is_background:
            self.is_run = True
            self.background = threading.Thread(target=self.read_thread)
            self.background.start()


    def read_thread(self):
        while self.is_run:
            try:
                self.read_one()
            except:
                traceback.print_exc()
                time.sleep(0.04)
            time.sleep(self.background_sleep_time)


    def read(self):
        if  self.with_frame_num:
            if self.is_background:
                return self.frame, self.frame_num
            else:
                return self.read_one()
        else:
            if self.is_background:
                return self.frame
            else:
                return self.read_one()[0]

    def read_one(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(self.device)
            if not self.cap.isOpened():
                raise Exception('cap is not opened')
        ret, frame = self.cap.read()
        if (not ret) or (frame is None):
            return None
        if self.is_to_rgb:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.frame = frame
        self.frame_num += 1
        return self.frame, self.frame_num

    def stop(self):

        if self.is_background:
            self.is_run = False
            self.background.join()
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            cv2.destroyAllWindows()




if __name__ == '__main__':
    from zutils.utils import relative_project_path
    cap = VideoCapture(relative_project_path('src/x.mp4'), is_background=True, background_sleep_time=1/25, with_frame_num=True)
    for i in range(20):
        x, n = cap.read()
        if x is not None:
            print(n)
            x = cv2.resize(x, (200, 150))
            # print(len(x))
            cv2.imshow('xxx',x)
            cv2.waitKey(1)
        time.sleep(1/1)
    cap.stop()




















