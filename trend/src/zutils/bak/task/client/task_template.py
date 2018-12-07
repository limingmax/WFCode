import time
class TaskTemplateWithFrame:
    def run(self, frame):
        print('frame', frame)

    def sleep(self):
        time.sleep(0.01)


class TaskTemplateWithoutFrame:
    def run(self):
        pass
    def sleep(self):
        time.sleep(0.01)