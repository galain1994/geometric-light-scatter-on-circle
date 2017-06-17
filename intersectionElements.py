#/usr/bin/env python
# -*- coding=utf-8 -*-

from __future__ import division
from math import pi

__all__ = ['Circle', 'Light', 'Sphere']

class Circle(object):
    """
    @param:radius float
    @center_or_x: coordinates 圆心坐标的元组或x坐标
    @center_y: 圆心y坐标
    """
    def __init__(self, radius, center_or_x=(0,0), center_y=None):
        self.radius = radius
        if not center_y:
            self.center = center_or_x
        else:
            self.center = (center_or_x, center_y)
        if self.center[0]*self.center[0] + self.center[1]*self.center[1] < radius*radius:
            self.center = (0, 0)

    def on_circle(self, point, tol=1e-5):
        left = pow(point[0]-self.center[0], 2)+pow(point[1]-self.center[1], 2)
        right = self.radius*self.radius
        if abs(left-right) < tol:
            return True
        return False


class Light(object):
    """
    定义光线的类
    @wavelength: 波长
    @direction:  方向 Vec2d 或者 Vec3d
    @refraction_index: 折射率
    @unit: 单位可选 nm, um, mm, cm
    """
    def __init__(self, wavelength, direction, refraction_index=1, unit='mm'):
        units = {'nm':1e-6, 'um':1e-3, 'mm':1, 'cm':1e3}
        if unit not in units.keys():
            raise ValueError('Use correct unit in {0}'.format(list(units.keys())))
        self.unit = unit
        self.wavelength = wavelength * units[unit]    # unit: mm
        self.refraction_index = refraction_index
        self.direction = direction.normalized()
        self.k = Light.wavenum(self.wavelength, refraction_index)
        self.k_vector = self.k * self.direction

    def __repr__(self):
        direction = tuple(i for i in self.direction)
        return "Light({0}):{1}".format(self.k, direction)

    @classmethod
    def wavenum(self, wavelength, refraction_index):
        k = 2*pi*refraction_index/wavelength
        return k


class Sphere(object):
    """
    定义球的类
    @param:radius float
    @center_or_x:传入圆心x，y，z的元组或者x坐标
    @center_y:圆心y坐标
    @center_z:圆心z坐标
    """
    def __init__(self, radius, center_or_x=(0, 0, 0), center_y=None, center_z=None):
        self.radius = radius
        if not center_y or center_z:
            self.center = center_or_x
        else:
            self.center = (center_or_x, center_y, center_z)

    def on_sphere(self, point, tol=1e-5):
        left = (pow(point[i]-self.center[i], 2) for i in range(3))
        if abs(sum(left)-pow(self.radius, 2)) < tol:
            return True
        return False







