'''
将Kitti点云数据与对应的rgb图像上的点相匹配
'''
import pykitti
import numpy as np
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
velo = data.velo

'''
转换关系:
Pcam = Pvel*T_cam_velo  #这里先要做个转换，将Pvel第4列全部变为1才可以计算（齐次）
Puv = K*Pcam/Zc  # 这里要将Pcam前三列取出，因为K是3×3矩阵
'''
point_velo_array = next(velo)
point_velo_array[:, 3] = 1 # 
mask = point_velo_array[:, 0] > 5

point_velo_array = point_velo_array[mask] # 去除小于图像平面5米的点
point_cam0 = data.calib.T_cam0_velo.dot(point_velo_array.T).T
point_piexl = data.calib.K_cam0.dot(point_cam0[:, : - 1].T).T
shape = point_cam0.shape
point_piexl = point_piexl / point_cam0[:, 2].reshape(shape[0], 1).repeat(3, 1) # 得到的是[n,3]矩阵

