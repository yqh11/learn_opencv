# -*- coding: utf-8 -*-
"""
Created on Mon Oct 19 17:57:48 2020

@author: dell
"""


# import tensorflow as tf
# import os
# import numpy as np
# from PIL import Image
# import matplotlib.pyplot as plt
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
#
# lines = tf.gfile.GFile('output_labels.txt').readlines()
# uid_to_human = {}
# for uid, line in enumerate(lines):
#     line = line.strip('\n')
#     uid_to_human[uid] = line
#
#
# def id_to_string(node_id):
#     if node_id not in uid_to_human:
#         return ''
#     return uid_to_human[node_id]
#
# with tf.gfile.FastGFile('output_graph.pb', 'rb') as f:
#     graph_def = tf.GraphDef()
#     graph_def.ParseFromString(f.read())
#     tf.import_graph_def(graph_def, name='')
#
#
# with tf.Session() as sess:
#
#     #print('1111111111111111111111111111111111111111111111111111111111111111111')
#     i = 0
#     for op in sess.graph.get_operations():
#         i = i + 1
#         if 1100 < i <= 1200:
#             print(op.name)
#         else:
#             pass
#     #print('2222222222222222222222222222222222222222222222222222222222222222222')
#     print(i)
#
#     '''
#     softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')
#
#     for root, dirs, files in os.walk('retrain/test_images'):
#         for file in files:
#             image_data = tf.gfile.FastGFile(os.path.join(root, file), 'rb').read()
#             predictions = sess.run(softmax_tensor, {'image_tensor:0': image_data})
#             predictions = np.squeeze(predictions)
#
#             image_path = os.path.join(root, file)
#             print(image_path)
#             img = Image.open(image_path)
#             plt.imshow(img)
#             plt.axis('off')
#             plt.show()
#
#             top_k = predictions.argsort()[::-1]
#             print(top_k)
#             for node_id in top_k:
#                 human_string = id_to_string(node_id)
#                 score = predictions[node_id]
#                 print('%s (score = %.5f)' % (human_string, score))
#             print()
#
#     '''



# # coding: utf-8
#
import tensorflow as tf

import os

import numpy as np

import re

from PIL import Image

import matplotlib.pyplot as plt
DATA_DIRECTORY = 'retrain/output_labels.txt'
if not tf.io.gfile.exists(DATA_DIRECTORY):
    tf.io.gfile.makedirs(DATA_DIRECTORY)
with tf.io.gfile.GFile('retrain/output_labels.txt') as f:
    lines = tf.io.gfile.GFile('retrain/output_labels.txt').readlines()

uid_to_human = {}

# 一行一行读取数据

for uid, line in enumerate(lines):
    # 去掉换行符

    line = line.strip('\n')

    uid_to_human[uid] = line


def id_to_string(node_id):
    if node_id not in uid_to_human:
        return ''

    return uid_to_human[node_id]


# 创建一个图来存放google训练好的模型

with tf.io.gfile.GFile('output_graph.pb', 'rb') as f:
    graph_def = tf.GraphDef()

    graph_def.ParseFromString(f.read())

    tf.import_graph_def(graph_def, name='')

with tf.Session() as sess:
    softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')

    # 遍历目录

    for root, dirs, files in os.walk('retrain/images/'):  # 测试图片存放位置

        for file in files:

            # 载入图片

            image_data = tf.gfile.FastGFile(os.path.join(root, file), 'rb').read()

            predictions = sess.run(softmax_tensor, {'DecodeJpeg/contents:0': image_data})  # 图片格式是jpg格式

            predictions = np.squeeze(predictions)  # 把结果转为1维数据

            # 打印图片路径及名称

            image_path = os.path.join(root, file)

            print(image_path)

            # 显示图片

            img = Image.open(image_path)

            plt.imshow(img)

            plt.axis('off')

            plt.show()

            # 排序

            top_k = predictions.argsort()[::-1]

            print(top_k)

            for node_id in top_k:
                # 获取分类名称

                human_string = id_to_string(node_id)

                # 获取该分类的置信度

                score = predictions[node_id]

                print('%s (score = %.5f)' % (human_string, score))

            print()






