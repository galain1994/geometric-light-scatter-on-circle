#/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import division
import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
from mpl_toolkits.mplot3d import art3d
from pygameVector import Vec3d
from funcs3d import *
from intersectionElements import Sphere, Light


def generate_sphere_cordinates(radius, longitude, latitude):
    longitude = complex(0, longitude)
    latitude = complex(0, latitude)
    u, v = np.mgrid[0:2*np.pi:longitude, 0:np.pi:latitude]
    x = radius * np.cos(u)*np.sin(v)
    y = radius * np.sin(u)*np.sin(v)
    z = radius * np.cos(v)
    return (x, y, z)


def draw_line(s, e):
    return art3d.Line3D((s[0], e[0]), (s[1], e[1]), (s[2], e[2]))


def main():
    import pprint

    radius = 10
    sphere = Sphere(radius, (0, 0, 0))

    v = Vec3d(0, 1, 0)
    light = Light(532, v, 1, unit='nm')
    refraction_index = 1.335

    x = 0
    y = -15
    z = 6
    start_point = (x, y, z)

    points = []
    lines = []

    first_intersection_point = calculate_first_intersection(sphere, start_point)
    line1 = draw_line(start_point, first_intersection_point)
    lines.append(line1)

    points.append(start_point)
    points.append(first_intersection_point)

    reflection_light = reflection(sphere, light, first_intersection_point)
    refraction_light = refraction(sphere, light, first_intersection_point, refraction_index)

    second_intersection_point = calculate_intersection_on_sphere(sphere, refraction_light, first_intersection_point)[1]
    points.append(second_intersection_point)

    line2 = draw_line(first_intersection_point, second_intersection_point)
    lines.append(line2)

    points = list(zip(*points))

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(*points)

    for line in lines:
        ax.add_line(line)

    x, y, z = generate_sphere_cordinates(10, 50, 20)
    # ax.plot_wireframe(x, y, z, color='r')
    alpha = 0.1
    ax.plot_surface(x, y, z, color='r', alpha=alpha)
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')
    plt.show()


if __name__ == '__main__':
    main()

