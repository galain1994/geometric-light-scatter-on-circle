#/usr/bin/env python
# -*- coding=utf-8 -*-

from __future__ import division
from math import pi
from pygameVector import Vec2d


class Circle(object):
    '''
    @param:radius float
    @center_or_x
    '''
    def __init__(self, radius, center_or_x=(0,0), center_y=None):
        self.radius = radius
        if not center_y:
            self.center = center_or_x
        else:
            self.center = (center_or_x, center_y)

    def on_circle(self, point, tol=1e-5):
        left = pow(point[0]-self.center[0], 2)+pow(point[1]-self.center[1], 2)
        right = self.radius*self.radius
        if abs(left-right) < tol:
            return True
        return False


class Line(object):

    def __init__(self, a_or_point_a, b_or_point_b, c=None):
        if not c:
            self.point_a = a_or_point_a
            self.point_b = b_or_point_b
            self._line_two_points()
        else:
            self.a, self.b, self.c = a_or_point_a, b_or_point_b, c

    def _line_two_points(self):
        # regular equation of the line
        x1, y1 = self.point_a
        x2, y2 = self.point_b
        self.a = y2 - y1
        self.b = x1 - x2
        self.c = x1*y2 - x2*y1

    def on_line(self, point, tol=1e-5):
        # check if point on the line
        left = self.a * point[0] + self.b * point[1]
        right = self.c
        if abs(right - left) < tol:
            return True
        return False


class intersectionDirection(object):

    def __init__(self, vertical_vec, tangen_vec, ):
        pass


class Light(object):

    def __init__(self, wavelength, direction, refraction_index=1, unit='mm'):
        units = {'nm':1e-6, 'um':1e-3, 'mm':1, 'cm':1e3}
        if unit not in units.keys():
            raise ValueError('Use correct unit in {0}'.format(list(units.keys())))
        self.unit = unit
        self.wavelength = wavelength * units[unit]    # unit: mm
        self.refraction_index = refraction_index
        self.direction = direction.normalized()
        self.k = Light.wavenum(self.wavelength, refraction_index)

    @classmethod
    def wavenum(self, wavelength, refraction_index):
        k = 2*pi*refraction_index/wavelength
        return k