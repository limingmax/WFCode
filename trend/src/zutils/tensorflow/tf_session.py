# @Time   : 2018-9-10
# @Author : zxh
import os
import tensorflow as tf

class TFSession:
    def __init__(self, cuda='0', gpu_mem=0.2, allow_growth=False):
        os.environ["CUDA_VISIBLE_DEVICES"] = cuda
        if allow_growth:
            tf_config = tf.ConfigProto(log_device_placement=False,
                                       allow_soft_placement=True,
                                       gpu_options=tf.GPUOptions(allow_growth=True))
        else:
            tf_config = tf.ConfigProto(log_device_placement=False,
                                       allow_soft_placement=True,
                                       gpu_options=tf.GPUOptions(per_process_gpu_memory_fraction=gpu_mem))
        self.sess = tf.InteractiveSession(config=tf_config)

    def get_sess(self):
        return self.sess