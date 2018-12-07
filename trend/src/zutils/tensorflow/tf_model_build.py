# @Time   : 2018-9-10
# @Author : zxh
import tensorflow as tf
import tensorlayer as tl
from zutils.tensorflow.tf_session import TFSession
import numpy as np
from tensorlayer.layers import DenseLayer
from tensorflow.python.framework.ops import get_name_scope
from inspect import isfunction


class TFModelBuild:
    def __init__(self, model_name, network_func):
        self.model_name = model_name
        self.network_func = network_func
        self.resue = False
        self.op_set = dict()
        self.op_set['train'] = dict()
        self.op_set['test'] = dict()

    def get_resue(self):
        resue = self.resue
        self.resue = True
        return resue

    def inference(self, inputs, n_classes):
        if (get_name_scope() != 'train') and (get_name_scope() != 'test'):
            raise Exception('name_scope is not train or test')

        reuse = self.get_resue()
        inputs = tf.identity(inputs, 'placeholder_inputs')

        op_ = self.op_set[get_name_scope()]
        with tf.variable_scope(self.model_name, reuse=reuse):
            tl.layers.set_name_reuse(reuse)
            network = self.network_func(inputs, get_name_scope() == 'train')
            op_['step'] = tf.get_variable(name='train_step', shape=(), dtype=tf.int32)
            op_['update_step'] = tf.assign(op_['step'], tf.add(op_['step'], tf.constant(1),
                                                            name='train_step_add_one'),
                                                            name='update_train_step')
            op_['network'] = DenseLayer(network, n_units=n_classes, act=tl.activation.identity, name='logits')

        op_['logits'] = op_['network'].outputs
        op_['softmax_logits'] = tf.nn.softmax(op_['logits'])
        op_['result'] = tf.argmax(op_['logits'], 1)
        return self


    def accuracy(self, labels, n_classes):
        if (get_name_scope() != 'train') and (get_name_scope() != 'test'):
            raise Exception('name_scope is not train or test')

        op_ = self.op_set[get_name_scope()]
        op_['total_accuracy'] = tf.reduce_mean(tf.cast(tf.equal(tf.argmax(op_['logits'], 1), labels), tf.float32))
        op_['class_accuracy'] = list()
        for c in range(n_classes):
            tindex = tf.reshape(tf.where(tf.equal(labels, c)), [-1])
            tlables = tf.nn.embedding_lookup(labels, tindex)
            toutput = tf.nn.embedding_lookup(op_['logits'], tindex)
            tacc = tf.reduce_mean(tf.cast(tf.equal(tf.argmax(toutput, 1), tlables), tf.float32))
            op_['class_accuracy'].append(tacc)

        return self



    def loss(self, labels):
        if (get_name_scope() != 'train') and (get_name_scope() != 'test'):
            raise Exception('name_scope is not train or test')

        op_ = self.op_set[get_name_scope()]
        op_['loss'] = tl.cost.cross_entropy(op_['logits'], labels, name='xentropy')
        return self

    def optimizer(self, learning_rate):
        if (get_name_scope() != 'train') and (get_name_scope() != 'test'):
            raise Exception('name_scope is not train or test')
        op_ = self.op_set[get_name_scope()]
        optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
        op_['train_op'] = optimizer.minimize(op_['loss'])
        return self




