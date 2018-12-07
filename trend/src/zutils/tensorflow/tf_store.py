# @Time   : 2018-9-10
# @Author : zxh
import os
import tensorflow as tf
import sys
from zutils.utils import relative_project_path

class TFStore:
    def __init__(self, sess, model_name, net_name, max_to_keep=500):
        self.sess = sess
        self.model_name= model_name
        self.net_name = net_name
        self.saver = tf.train.Saver(max_to_keep=0)

    def relative_model_dir_path(self, *paths):
        return relative_project_path('models', self.model_name, self.net_name, *paths)

    def load_model(self, step):
        if not os.path.isfile(self.relative_model_dir_path(str(step), 'model.meta')):
            raise Exception('model is not exist')
        self.saver.restore(self.sess, self.relative_model_dir_path(str(step), 'model'))
        print('restore model succeed, path:', self.relative_model_dir_path(str(step), 'model'))


    def init_model(self):
        tf.global_variables_initializer().run()
        print('init model succeed')


    def load_or_init_model(self, step):
        if os.path.isfile(self.relative_model_dir_path(str(step), 'model.meta')):
            self.saver.restore(self.sess, self.relative_model_dir_path(str(step), 'model'))
            print('restore model succeed, path:', self.relative_model_dir_path(str(step), 'model'))
        else:
            tf.global_variables_initializer().run()
            print('init model succeed')


    def save_model(self, save_cur_step, save_0_step):
        with tf.variable_scope(self.model_name, reuse=True):
            step = tf.get_variable('train_step', shape=(), dtype=tf.int32).eval()
        if save_cur_step:
            os.makedirs(self.relative_model_dir_path(str(step)), exist_ok=True)
            self.saver.save(self.sess, self.relative_model_dir_path(str(step), 'model'))
            print('save model succeed, step:', step)
        if save_0_step:
            step = 0
            os.makedirs(self.relative_model_dir_path(str(step)), exist_ok=True)
            self.saver.save(self.sess, self.relative_model_dir_path(str(step), 'model'))
            print('save model succeed, step:', step)



    def create_tensorboard_write(self):
        tensorboard_path = self.relative_model_dir_path('tensorboard')
        os.makedirs(tensorboard_path, exist_ok=True)
        return tf.summary.FileWriter(tensorboard_path, self.sess.graph)

    def check_close_file(self):
        return os.path.isfile(self.relative_model_dir_path('close'))

    def remove_close_file(self):
        if os.path.isfile(self.relative_model_dir_path('close')):
            os.remove(self.relative_model_dir_path('close'))
            return True
        return False
