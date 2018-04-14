"""
+ 将图片组合成视频
"""
# import tensorflow as tf
import numpy as np
import scipy.misc
import cv2
import matplotlib.pyplot as plt
import os
import argparse
original_height = 370
original_width = 1226
parser = argparse.ArgumentParser()
parser.add_argument('--mode', type=str, help='e or r', default='e')
parser.add_argument('--image_path',type=str,default='./')
args = parser.parse_args()

def npy_to_png():
    disp_list = np.load('disparities_pp.npy')
    i = 0
    for disp in disp_list:
        disp_to_img = scipy.misc.imresize(disp, [original_height, original_width])
        plt.imsave(os.path.join('/media/ccb/CCB/data/disp', "{}_disp.jpg".format(str(i))), disp_to_img, cmap='plasma')
        i += 1

def transform_jpg_to_video():
    fps = 30   #视频帧率
    fourcc = cv2.VideoWriter_fourcc( * 'MJPG')
    picList = sorted(os.listdir(args.image_path))
    videoWriter = cv2.VideoWriter(os.path.join(args.image_path, 'flower.avi'), fourcc, fps, (original_width, original_height))
    for pic in picList:
        if pic.split('.')[-1] =='png' or pic.split('.')[-1] =='jpg':
            img12 = cv2.imread(os.path.join(args.image_path, pic))
            videoWriter.write(img12)
    videoWriter.release()


if __name__ == '__main__':
    if args.mode == 'e':
        npy_to_png()
    if args.mode == 'r':    
        transform_jpg_to_video()