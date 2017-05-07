#/usr/bin/env python
# -*- coding:utf-8 -*-

from pygameVector import Vec3d

def compution_on_intersection(circle, light, intersection_point):

    def convert_to_rectangular_coordinate(vertical, tangen):
        # compute the transform factor
        m11 = BASIC_X_AXIS_VECTOR.dot(vertical)
        m12 = BASIC_X_AXIS_VECTOR.dot(tangen)
        m21 = BASIC_Y_AXIS_VECTOR.dot(vertical)
        m22 = BASIC_Y_AXIS_VECTOR.dot(tangen)
        C = matrix([[m11, m12], [m21, m22]])
        return C

    center = circle.center
    radius = circle.radius

    direction = light.direction
    vertical = Vec3d(intersection_point).normalized()
