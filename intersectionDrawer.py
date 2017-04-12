#/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import division
import matplotlib.pyplot as plt
from matplotlib import lines
from pygameVector import Vec2d
from intersectionElements import Circle, Line, Light
from intersectionFuncs import intersection, reflection, refraction


def draw_linesegment(start_point, end_point, color):
    # draw line from to point coordinates
    x = (start_point[0], end_point[0])
    y = (start_point[1], end_point[1])
    line = lines.Line2D(x, y, color=color)
    return line


def light_reflection_outside(circle, light, start_point, color='b'):
    # outside the circle; the reflection
    vector = light.direction
    vectortimes = vector * 30
    end_point = (start_point[0] + vectortimes.x, start_point[1] + vectortimes.y)
    line = draw_linesegment(start_point, end_point, color)
    return line


def light_intersection(circle, light, start_point, color='b'):
    # draw from Light class
    vector = light.direction
    intersection_point = intersection(circle, light.direction, start_point)
    end_point = intersection_point[0]
    line = draw_linesegment(start_point, end_point, color)
    return line


def main():
    radius = 1
    circle = Circle(radius, (0, 0))
    density = 20
    # initial the incident light
    start_point_list = [(-15, i*(radius/density)) for i in range((-density), density)]
    vector = Vec2d(3, 4).normalized()

    intersection_point_list = []
    for p in start_point_list:
        inter_point_left = intersection(circle, vector, p)[0]
        intersection_point_list.append(inter_point_left)

    # axes, figure, plot, scatter test
    fig, ax = plt.subplots(1, 1)
    xy = tuple(zip(*intersection_point_list))
    fig = plt.scatter(xy[0], xy[1])
    circle_plot = plt.Circle((0, 0), radius, fill=False)
    plt.gca().add_patch(circle_plot)

    # line segment test
    incident_light = Light(532, vector, 1, unit='nm')

    reflection_lights = [reflection(circle, incident_light, start_point) for start_point in start_point_list]
    refraction_lights = [refraction(circle, incident_light, start_point, 1.335) for start_point in start_point_list]

    incident_lines = [draw_linesegment(start_point, end_point, color='y') for (start_point, end_point) in zip(start_point_list, intersection_point_list)]
    reflection_lines = [light_reflection_outside(circle, reflection_light, intersection_point, color='b') \
                            for (reflection_light, intersection_point) in zip(reflection_lights, intersection_point_list)]
    refraction_lines = [light_intersection(circle, refraction_light, intersection_point, color='r') \
                            for (refraction_light, intersection_point) in zip(refraction_lights, intersection_point_list)]

    # add lines of incident/reflection/refraction ray to the plot
    for line in incident_lines[1:]:
        ax.add_line(line)
    for line in reflection_lines[1:]:
        ax.add_line(line)
    for line in refraction_lines[1:]:
        ax.add_line(line)

    plt.axis('equal')
    plt.axis([-1, 1, -1, 1])
    plt.show()


if __name__ == '__main__':
    main()