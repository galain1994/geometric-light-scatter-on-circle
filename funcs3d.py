#/usr/bin/env python
# -*- coding:utf-8 -*-

import math
from numpy import matrix
from pygameVector import Vec3d
from intersectionElements import Light, Sphere

__all__ = [ 'calculate_elevation_angle', 'calculate_intersection_on_sphere',
            'calculate_azimuth','reflection', 'refraction', 'ref_factors']  # 暴露给外部的函数


def calculate_elevation_angle(vector):
    """计算矢量在（x，y，z）坐标系下的抬升角
    """
    kx, ky, kz = vector
    return math.degrees(math.atan2(kz, math.sqrt(kx*kx+ky*ky)))

def calculate_azimuth(vector):
    kx, ky, kz = vector
    return math.degrees(math.atan2(kx, ky))


def calculate_intersection_on_sphere(sphere, light, start):
    """用与光线与球交点的求解
    """
    v = light.direction # 获取光线方向的矢量
    center_vector = Vec3d(sphere.center)
    radius = sphere.radius
    if Vec3d(0, 0, 0) == v: # 若矢量为0，返回None，避免除数为0
        return None
    if sphere.on_sphere(start):
        # 起点在球上，则顺序为（另一点， 起点）
        t = (-2) * (v.x*start[0] + v.y*start[1] + v.z*start[2]) / (v.x**2+v.y**2+v.z**2)
        end = start + t*v
        return (end, start)
    else:
        # 起点不在球上，顺序为（离起点较近的点， 离起点较远的点）
        # 与球没有交点，则返回None
        a = v.dot(v)
        b = 2*v.dot(start-center_vector)
        c = (start-center_vector).dot(start-center_vector) - radius*radius
        disc = b*b - 4*a*c
        if disc<0:
            return None
        sqrt_disc = math.sqrt(disc)
        t1 = (-b - sqrt_disc) / (2*a)
        t2 = (-b + sqrt_disc) / (2*a)
        return (start+t1*v, start+t2*v)
        

def ref_factors(sphere, light, intersection_point):
    """作用点处的计算（根据边界条件的公式）
    """
    center = sphere.center
    radius = sphere.radius

    k_li_vector = light.k_vector # 入射光的波矢量

    # vector on the surface of the intersection 作用点处建立的坐标系
    unit_n_vector = Vec3d(tuple((intersection_point[i]-center[i])/radius for i in range(3))).normalized()   # 单位化
    unit_b_vector = (light.direction.cross(unit_n_vector)).normalized()
    unit_t_vector = (unit_b_vector.cross(unit_n_vector)).normalized()
    c = matrix([unit_n_vector, unit_t_vector, unit_b_vector]).T   # 由该坐标系得到的矩阵C
 
    k_normal = k_li_vector.dot(unit_n_vector) # 入射光的法向分量
    k_tangen = k_li_vector.dot(unit_t_vector) # 入射光的切向分量

    return dict(c=c, tangen=k_tangen, normal=k_normal)


def reflection(factors, light):
    """计算反射光
    """
    wavelength = light.wavelength
    refraction_index = light.refraction_index   # 反射光的折射率和入射光相同

    # light factor 
    normal = (-1) * factors['normal']   # 反射光的法向分量
    tangen = factors['tangen']  # 反射光的切向分量
    c = factors['c']    # 获取矩阵C

    # reflection light vector
    direction = c * matrix([[normal], [tangen], [0]])   # 方向转化为（x，y，z）坐标系下的坐标表示
    direction = Vec3d(direction.A1).normalized()    # 转化为Vec3d矢量
    return Light(wavelength, direction, refraction_index)   # 返回该光线


def refraction(factors, light, refraction_index):
    """计算折射光
    """
    wavelength = light.wavelength
    k = Light.wavenum(wavelength, refraction_index) # 由入射光的波长和给定的折射率计算光波数

    normal_sgn = 1 if factors['normal'] > 0 else -1 # 折射光线在边界的另一侧（与入射光相比）
    tangen = factors['tangen']  # 折射光的切向分量
    normal = normal_sgn * math.sqrt(k*k-tangen*tangen) # 折射光的法向分量
    c = factors['c']    # 矩阵C

    direction = (c*matrix([[normal], [tangen], [0]])).A1    # 折射光的方向转化为（x，y，z）坐标系下的坐标表示
    direction = Vec3d(direction).normalized()
    return Light(wavelength, direction, refraction_index)











