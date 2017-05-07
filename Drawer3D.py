#/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import division
import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
from mpl_toolkits.mplot3d import art3d


def generate_sphere_cordinates(radius, longitude, latitude):
    longitude = complex(0, longitude)
    latitude = complex(0, latitude)
    u, v = np.mgrid[0:2*np.pi:longitude, 0:np.pi:latitude]
    x = radius * np.cos(u)*np.sin(v)
    y = radius * np.sin(u)*np.sin(v)
    z = radius * np.cos(v)
    return (x, y, z)


def generate_start_points(radius, y, amount, tol=1e-2):
    points = []
    step = 2 * radius / (amount - 1)
    negative_radius = (-1) * radius
    spansion = [negative_radius+i*step for i in range(amount)]
    spansion[0] = negative_radius + tol
    spansion[-1] = radius - tol
    for i in range(amount):
        for j in range(amount):
            points.append((spansion[j], y, spansion[i]))
    return points


def calculate_first_intersection(start_point, radius):
    x = start_point[0]
    z = start_point[2]
    v = math.acos(z/radius)
    try:
        u = math.acos((x/(radius*math.sin(v)))) + math.pi
    except ValueError:
        return None
    else:
        intersection_y = radius * math.sin(u) * math.sin(v)
        return (x, intersection_y, z)


def main():
    import pprint
    radius = 10
    y = -15
    amount = 5
    m = generate_start_points(radius, y, amount)
    mm = list(zip(*m))          # include three list:x, y, z coordinates


    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(*mm)

    intersection_points = [calculate_first_intersection(start_point, radius) for start_point in m]

    lines = [art3d.Line3D((s[0], e[0]), (s[1], e[1]), (s[2], e[2])) for (s, e) in zip(m, intersection_points) if e is not None]
    for line in lines:
        ax.add_line(line)

    intersection_points = [i for i in intersection_points if i is not None]
    intersection_points = list(zip(*intersection_points))
    ax.scatter(*intersection_points)

    x, y, z = generate_sphere_cordinates(10, 50, 20)
    # ax.plot_wireframe(x, y, z, color='r')
    alpha = 0.1
    ax.plot_surface(x, y, z, color='b', alpha=alpha)
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')
    plt.show()


if __name__ == '__main__':
    main()