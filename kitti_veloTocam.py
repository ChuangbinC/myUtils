'''
将Kitti点云数据与对应的rgb图像上的像素对齐

这个脚本是针对一个点云图和一张RGB 如果要处理全部请修改一下就可以
'''
import pykitti
import numpy as np

import scipy.misc
import matplotlib.pyplot as plt
import cv2
basedir = '/home/ccb/下载' 
date = '2011_09_26'
drive = '0001'

# The 'frames' argument is optional - default: None, which loads the whole dataset.
# Calibration and timestamp data are read automatically. 
# Other sensor data (cameras, IMU, Velodyne) are available via properties 
# that create generators when accessed.
data = pykitti.raw(basedir, date, drive, frames=range(0, 50, 5))

# dataset.calib:      Calibration data are accessible as a named tuple
# dataset.timestamps: Timestamps are parsed into a list of datetime objects
# dataset.oxts:       Returns a generator that loads OXTS packets as named tuples
# dataset.camN:       Returns a generator that loads individual images from camera N
# dataset.gray:       Returns a generator that loads monochrome stereo pairs (cam0, cam1)
# dataset.rgb:        Returns a generator that loads RGB stereo pairs (cam2, cam3)
# dataset.velo:       Returns a generator that loads velodyne scans as [x,y,z,reflectance]

velo = data.velo # 这个是一个generator
'''
转换关系:
Pcam = Pvel*T_cam_velo  #这里先要做个转换，将Pvel第4列全部变为1才可以计算（齐次）
Puv = K*Pcam/Zc  # 这里要将Pcam前三列取出，因为K是3×3矩阵
'''
point_velo_array = next(velo)
point_velo_array[:, 3] = 1 # 将第三列变为一，为了矩阵计算
mask = point_velo_array[:, 0] > 5
point_velo_array = point_velo_array[mask] # 去除小于图像平面5米的点，kitti官方matlab脚本有，原因不清楚
point_velo_array = point_velo_array[::5]  # 间隔取点，不要那么密集，可以注释掉
point_cam0 = data.calib.T_cam0_velo.dot(point_velo_array.T).T # 这里用的是velo到cam0的转换关系
point_piexl = data.calib.K_cam0.dot(point_cam0[:, : - 1].T).T[:, 0: - 1] # point_cam0[:, 2]就是深度
shape = point_piexl.shape
point_piexl = point_piexl / point_cam0[:, 2].reshape(shape[0], 1).repeat(2, 1) # 得到的是[n,2]矩阵 (u,v)像素坐标
cloud_point = np.column_stack((point_piexl, point_cam0[:, 2])) # 得到一个[n,3]矩阵，第三列为雷达深度
# 像素坐标 应为整数，所以这里可以对 第一，二列进行int处理，看情况而定

'''
如果velo跟rgb图片都要缩放，velo图就不能够使用cv或者其他的resize函数，因为他们使用的是内插法
'''
def pic_resize(a, width, height):
    a[:,0] = a[:,0]/width*512 # 512 256 是 毕设论文要求，根据情况修改
    a[:,1] = a[:,1]/height*256
    return a

# rgb图像是[375,1242]
mask = cloud_point[:, 0] > 0
cloud_point = cloud_point[mask] 

mask = cloud_point[:, 0] < 1241 
cloud_point = cloud_point[mask] # 落在 0 < width < 1242的点云

mask = cloud_point[:, 1] > 0
cloud_point = cloud_point[mask]

mask = cloud_point[:, 1] < 374
cloud_point = cloud_point[mask]# 落在 0 < height < 375的点云 

cloud_point = pic_resize(cloud_point,1242,375) # 缩小图像 
cloud_point = cloud_point.astype(int)


trap = np.zeros((256, 512)) # 将点云对应到 一张图片上 效果如图是
for h,w,depth in cloud_point:
    trap[h, w] = depth
trap = np.expand_dims(trap, axis=2)

