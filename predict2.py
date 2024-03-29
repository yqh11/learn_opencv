# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 09:59:23 2020

@author: dell
"""



from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse

import numpy as np
import tensorflow as tf

import os

def load_graph(model_file):
  graph = tf.Graph()
  graph_def = tf.compat.v1.GraphDef()

  with open(model_file, "rb") as f:
    graph_def.ParseFromString(f.read())
  with graph.as_default():
    tf.import_graph_def(graph_def)

  return graph

def read_tensor_from_image_file(file_name,
                                input_height=299,
                                input_width=299,
                                input_mean=0,
                                input_std=255):
  input_name = "file_reader"
  output_name = "normalized"
  file_reader = tf.io.read_file(file_name, input_name)
  if file_name.endswith(".png"):
    image_reader = tf.image.decode_png(
        file_reader, channels=3, name="png_reader")
  elif file_name.endswith(".gif"):
    image_reader = tf.squeeze(
        tf.image.decode_gif(file_reader, name="gif_reader"))
  elif file_name.endswith(".bmp"):
    image_reader = tf.image.decode_bmp(file_reader, name="bmp_reader")
  else:
    image_reader = tf.image.decode_jpeg(
        file_reader, channels=3, name="jpeg_reader")
  float_caster = tf.cast(image_reader, tf.float32)
  dims_expander = tf.expand_dims(float_caster, 0)
  resized = tf.compat.v1.image.resize_bilinear(dims_expander, [input_height, input_width])
  normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
  sess = tf.compat.v1.Session()
  result = sess.run(normalized)

  return result


def load_labels(label_file):
  label = []
  proto_as_ascii_lines = tf.io.gfile.GFile(label_file).readlines()
  for l in proto_as_ascii_lines:
    label.append(l.rstrip())
  return label


if __name__ == "__main__":

  file_name = " "
  image_path = './retrain_car/test_images'  # 测试图片文件夹
  model_file = './car_graph.pb'  # retrain.py 生成的output_graph.pb
  label_file = "./car_labels.txt"             # retrain.py 生成的output_labels.txt
  input_height = 299
  input_width = 299
  input_mean = 0
  input_std = 255
  input_layer = "Placeholder"
  output_layer = "final_result"

  parser = argparse.ArgumentParser()
  parser.add_argument("--image", help="image to be processed")
  parser.add_argument("--graph", help="graph/model to be executed")
  parser.add_argument("--labels", help="name of file containing labels")
  parser.add_argument("--input_height", type=int, help="input height")
  parser.add_argument("--input_width", type=int, help="input width")
  parser.add_argument("--input_mean", type=int, help="input mean")
  parser.add_argument("--input_std", type=int, help="input std")
  parser.add_argument("--input_layer", help="name of input layer")
  parser.add_argument("--output_layer", help="name of output layer")
  args = parser.parse_args()

  graph = load_graph(model_file)

  input_name = "import/" + input_layer
  output_name = "import/" + output_layer
  input_operation = graph.get_operation_by_name(input_name)
  output_operation = graph.get_operation_by_name(output_name)

  with tf.compat.v1.Session(graph=graph) as sess:

    for root, dirs, files in os.walk(image_path):
      for file in files:
        if file.endswith('.png') or file.endswith('.gif') or file.endswith('.bmp') \
                or file.endswith('.jpg') or file.endswith('.gif'):
          file_name = os.path.join(image_path, file)

          t = read_tensor_from_image_file(
            file_name,
            input_height=input_height,
            input_width=input_width,
            input_mean=input_mean,
            input_std=input_std)

          results = sess.run(output_operation.outputs[0], {
              input_operation.outputs[0]: t
          })

          results = np.squeeze(results)
          top_k = results.argsort()[-5:][::-1]
          labels = load_labels(label_file)
          predictions_list = []
          for i in top_k:
            predictions_list.append([labels[i], results[i]])
          #print(file_name, '\n', predictions_list, '\n')
          best_pred = predictions_list[0]
          pred_label = best_pred[0]
          pred_score = best_pred[1]
          print(pred_label)
          print(pred_score)

