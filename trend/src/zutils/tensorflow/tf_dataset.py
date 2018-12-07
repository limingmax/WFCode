# @Time   : 2018-9-10
# @Author : zxh
import tensorflow as tf
import numpy as np
from scipy import misc
from zutils.image import normalization_image, random_rotate_image



class TFDataset:

    def __init__(self, image_list, label_list, image_size, batch_size, capacity=500):
        temp = np.array([image_list, label_list])
        temp = temp.transpose()
        np.random.shuffle(temp)

        # 从打乱的temp中再取出list（img和lab）
        image_list = list(temp[:, 0])
        label_list = list(temp[:, 1])
        label_list = [int(i) for i in label_list]

        n = len(image_list)
        if n < 15000:
            train_n = n // 10 * 9
        else:
            train_n = n - 1500
        self.test_image_list = image_list[train_n:]
        self.test_label_list = label_list[train_n:]

        image_list = image_list[: n // 10 * 9]
        label_list = label_list[: n // 10 * 9]

        image = tf.cast(image_list, tf.string)
        label = tf.cast(label_list, tf.int64)
        input_queue = tf.train.slice_input_producer([image, label])
        # 加入队列
        label = input_queue[1]
        image_contents = tf.read_file(input_queue[0])
        image = tf.image.decode_jpeg(image_contents, channels=3)
        # image = tf.image.resize_images(image, [image_size_big, image_size_big])

        # jpeg或者jpg格式都用decode_jpeg函数，其他格式可以去查看官方文档
        image = tf.py_func(random_rotate_image, [image], tf.uint8)
        image = tf.random_crop(image, [image_size, image_size, 3])
        image = tf.image.random_flip_left_right(image)
        image.set_shape((image_size, image_size, 3))
        image = tf.image.per_image_standardization(image)
        image_batch, label_batch = tf.train.batch([image, label], batch_size=batch_size, num_threads=4,
                                                  capacity=capacity)
        label_batch = tf.reshape(label_batch, [batch_size])
        self.image_batch = image_batch
        self.label_batch = label_batch
        self.batch_size = batch_size
        self.image_size = image_size



    def get_train_batch(self):
        return self.image_batch, self.label_batch


    def get_test_batch(self):
        start = 0
        while start < len(self.test_image_list):
            image_batch_list = list()
            label_batch_list = list()
            for i in range(start, start + self.batch_size):
                if i >= len(self.test_image_list):
                    break
                arr = misc.imread(self.test_image_list[i])
                margin = (arr.shape[0] - self.image_size) // 2
                arr = arr[margin: margin + self.image_size, margin:margin + self.image_size, :]
                arr = normalization_image(arr)
                image_batch_list.append(arr)
                label_batch_list.append(self.test_label_list[i])
            start = start + self.batch_size
            yield np.stack(image_batch_list), np.stack(label_batch_list)

#
# def get_train_batch(image_list,label_list, image_size, batch_size, capacity):
#     # 利用shuffle打乱顺序
#     temp = np.array([image_list, label_list])
#     temp = temp.transpose()
#     np.random.shuffle(temp)
#
#     # 从打乱的temp中再取出list（img和lab）
#     image_list = list(temp[:, 0])
#     label_list = list(temp[:, 1])
#     label_list = [int(i) for i in label_list]
#
#     n = len(image_list)
#     test_image_list = image_list[n // 10 * 9 :]
#     test_label_list = label_list[n // 10 * 9 :]
#
#     image_list = image_list[: n // 10 * 9]
#     label_list = label_list[: n // 10 * 9]
#
#
#     image = tf.cast(image_list,tf.string)
#     label = tf.cast(label_list,tf.int64)
#     input_queue = tf.train.slice_input_producer([image,label])
#     #加入队列
#     label = input_queue[1]
#     image_contents = tf.read_file(input_queue[0])
#     image = tf.image.decode_jpeg(image_contents,channels=3)
#     # image = tf.image.resize_images(image, [image_size_big, image_size_big])
#
#     #jpeg或者jpg格式都用decode_jpeg函数，其他格式可以去查看官方文档
#     image = tf.py_func(random_rotate_image, [image], tf.uint8)
#     image = tf.random_crop(image, [image_size, image_size, 3])
#     image = tf.image.random_flip_left_right(image)
#     image.set_shape((image_size, image_size, 3))
#     image = tf.image.per_image_standardization(image)
#     image_batch,label_batch = tf.train.batch([image,label],batch_size = batch_size,num_threads=4,capacity = capacity)
#     label_batch = tf.reshape(label_batch,[batch_size])
#     return image_batch,label_batch, test_image_list, test_label_list
#
#
# def get_test_batch(image_list, label_list, image_size, batch_size):
#
#
#     start = 0
#     while start < len(image_list):
#         image_batch_list = list()
#         label_batch_list = list()
#         for i in range(start, start + batch_size):
#             if i >= len(image_list):
#                 break
#             arr = misc.imread(image_list[i])
#             margin = (arr.shape[0] - image_size) // 2
#             arr = arr[margin: margin+image_size, margin:margin+image_size, :]
#             arr = normalization_image(arr)
#             image_batch_list.append(arr)
#             label_batch_list.append(label_list[i])
#         start = start + batch_size
#         yield np.stack(image_batch_list), np.stack(label_batch_list)
#
#