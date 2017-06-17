#/usr/bin/env python
# -*- coding=utf-8 -*-

from __future__ import division
import math
import decimal
from numpy import matrix, linspace
from pygameVector import Vec2d
from intersectionElements import Circle, Light

__all__ = ['tangential_vector_to_circle', 'intersection', 'reflection', 'refraction', 'pick_start_points']


def tangential_vector_to_circle(circle, start_point):
    """计算入射光线方向的范围 
    计算从左侧入射的光线（1，y）最小方向&最大方向，与圆相切的切线的向量
    @param:circle: instance of Circle
    @param:start_point: (x, y)
    @return: tuple
    """
    center = circle.center
    radius = circle.radius
    dx = center[0] - start_point[0]
    dy = center[1] - start_point[1] 
    dd = math.sqrt(dx*dx + dy*dy)
    if dd < radius:
        return None
    a = math.asin(radius/dd)
    b = math.atan2(dy, dx)

    # 顺时针一个角度，逆时针一个角度
    t1 = dict(x=radius*math.sin(b-a), y=radius*(-math.cos(b-a)))
    t2 = dict(x=radius*(-math.sin(b+a)), y=radius*math.cos(b+a))
    # 两个切点
    p1 = (center[0]+t1['x'], center[1]+t1['y'])
    p2 = (center[0]+t2['x'], center[1]+t2['y'])
    # 两条切线方向
    vector1 = Vec2d((p1[0]-start_point[0]), (p1[1]-start_point[1])).normalized()
    vector2 = Vec2d((p2[0]-start_point[0]), (p2[1]-start_point[1])).normalized()
    # 保留两位小数 切断其他位
    vector1 = Vec2d(1, decimal.Decimal(vector1.y/vector1.x).quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN))
    vector2 = Vec2d(1, decimal.Decimal(vector2.y/vector2.x).quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN))
    vector = (vector1, vector2) if vector2.y > vector1.y else (vector2, vector1) # 根据向量的y值大小排列
    return vector


def intersection(circle, vector, start_point):
    """计算向量与源的交点get circle attributes
    @param:circle: instance of Circle
    @param:vector: instance of Vec2d
    @param:start_point: vector or tuple of (x, y)
    @return: tuple
    """
    center = Vec2d(circle.center)
    radius = circle.radius

    start_point = Vec2d(start_point)
    # the params for calculating t 
    a = vector.dot(vector)
    b = 2 * (vector.dot(start_point - center))
    c = start_point.dot(start_point) + center.dot(center) - 2*start_point.dot(center) - pow(radius, 2)
    # judge if there's intersection 判别式 
    disc = b*b - 4*a*c
    if disc < 0:
        return None     # 判别式小于零则没有交点 返回None
    sqrt_disc = math.sqrt(disc)
    t1 = (-b - sqrt_disc) / (2*a)
    t2 = (-b + sqrt_disc) / (2*a)
    multi_factor = [x for x in (t1, t2) if abs(x) > 1e-6]   # filt the start point 如果起始点为交点之一则舍弃
    intersection = [start_point + t*vector for t in multi_factor]
    # left point & right point vector
    intersection_one = intersection[0]
    if len(intersection) > 1:
        intersection_two = intersection[1]
    else:
        # start point is one of the intersection point
        intersection_two = start_point
    return ((intersection_one.x, intersection_one.y), (intersection_two.x, intersection_two.y))


def pick_start_points(circle, vector, density, distance=2, tol=1e-2):
    """光簇起始点的生成
    @param:circle: instance of Circle
    @param:vector: instance of Vec2d
    @param:density: Number of Light
    @param:distance: times of length of radius
    @return: list
    """
    v = vector.rotated(90)   # calculate span vector
    p1, p2 = intersection(circle, v, circle.center)     # intersection point in the vertical direction of vector
    t_limits = (p2[0]-p1[0])/v.x if round(v.x) != 0 else (p2[1]-p1[1])/v.y     # max/min t that limits the span
    t_limits = t_limits + 1 if t_limits < 0 else t_limits            # close to the middle
    t_range = linspace(tol, t_limits-tol, density) if 0 < t_limits \
                else linspace(t_limits+tol, -tol, density)               # span of vector factor 决定范围的t的步长
    basic_point_v = Vec2d(p1) - vector*circle.radius*distance           # vector of the starting point
    start_points_v = [basic_point_v + t*v for t in t_range]             # collection of the start points vector
    start_points = [(p.x, p.y) for p in start_points_v]
    return start_points


def ref_factors(circle, incident_light, intersection_point):
    """calculate the C matrix and the K factor of the incident ray
    计算边界条件的参数 入射光线的分量和C矩阵
    @param:circle instance of Circle
    @param:incident_light instance of Light
    @param:intersection_point coordinate (x, y)
    @return: dict factors to calculation of the lights
    """
    def convert_to_rectangular_coordinate(vertical, tangen):
        # compute the transform factor
        # 计算C矩阵
        m11 = vertical.x
        m12 = tangen.x
        m21 = vertical.y
        m22 = tangen.y
        C = matrix([[m11, m12], [m21, m22]])
        return C

    center = circle.center
    radius = circle.radius 
    incident_vector = incident_light.k * incident_light.direction    # vector that represent the light direction

    _vec = Vec2d(intersection_point[0]-center[0], intersection_point[1]-center[1])
    angle = math.radians(_vec.angle)

    vertical_direction = Vec2d(math.cos(angle), math.sin(angle)).normalized()
    tangen_direction = Vec2d((-1)*math.sin(angle), math.cos(angle)).normalized()
    # the components of the incident ray
    incident_k_vertical = incident_vector.dot(vertical_direction)   # 法向
    incident_k_tangen = incident_vector.dot(tangen_direction)       # 切向
    # factor that determine the relection ray and refraction ray
    transform_factor = convert_to_rectangular_coordinate(vertical_direction, tangen_direction)

    return dict(c=transform_factor, tangen=incident_k_tangen, vertical=incident_k_vertical)


def reflection(factors, incident_light):
    """attributes of the incident_light
    计算反射光线 利用边界条件的结果
    @factors ref_factors 返回的字典
    @incident_light 光线的实例"""
    wavelength =  incident_light.wavelength
    refraction_index = incident_light.refraction_index
    
    # light direction
    # formula to calculate the K factor
    incident_k_vertical = (-1) * factors['vertical']
    incident_k_tangen = factors['tangen']
    direction = factors['c'] * matrix([[incident_k_vertical], [incident_k_tangen]])
    vector = Vec2d(direction.A1).normalized()
    return Light(wavelength, vector, refraction_index)


def refraction(factors, incident_light, refraction_index):
    """attributes of the incident_light
    计算折射光线 利用边界条件的结果
    """
    wavelength = incident_light.wavelength
    
    # refraction light direction
    # formula
    wavenum = Light.wavenum(wavelength, refraction_index)
    incident_k_vertical = factors['vertical']
    incident_k_tangen = factors['tangen']
    sign = 1 if incident_k_vertical > 0 else -1         # 法线方向的符号和入射光线相同
    kt_vertical = sign * math.sqrt(wavenum*wavenum - incident_k_tangen*incident_k_tangen)    # 法线方向
    direction = factors['c'] * matrix([[kt_vertical], [incident_k_tangen]])
    vector = Vec2d(direction.A1).normalized()
    return Light(wavelength, vector, refraction_index)


