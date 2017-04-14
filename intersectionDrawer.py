#/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import division
import matplotlib.pyplot as plt
from matplotlib import lines
from pygameVector import Vec2d
from intersectionElements import Circle, Line, Light
from intersectionFuncs import intersection, reflection, refraction, pick_start_points

COLORS = ['#FF0033', '#FF6600', '#FFFF33', '#33FF33',
          '#00FFFF', '#006666', '#CC00CC', '#000000', '#CCCCCC']    # red, orange, yellow, green, blue, navy, purple, black, silver

def draw_linesegment(start_point, end_point, color):
    # draw line from to point coordinates
    x = (start_point[0], end_point[0])
    y = (start_point[1], end_point[1])
    line = lines.Line2D(x, y, color=color)
    return line


def light_reflection_outside(circle, light, start_point, color='b', times=2):
    # outside the circle; the reflection
    vector = light.direction
    vectortimes = vector.normalized() * circle.radius * times
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


def drawer(circle, incident_ray, density, refraction_index, outside_ref_index=1, intersection_time=1, distance=2, tol=1e-2, start_point=None):
    '''

    @param:circle
    @param:
    @param:
    @param:
    @param:intersection_time    how many time the light intersect the circle
    @param:distance             how many times of line expand multiply by the radius
    @param:tol                  the distance to the boarder of the circle
    @param:
    '''
    if not isinstance(intersection_time, int) or intersection_time < 1:
        raise ValueError('Intersection times should not be less than 1 and should be int')

    radius = circle.radius
    center = circle.center
    incident_ray_vector = incident_ray.direction.normalized()

    if not start_point:
        start_points = pick_start_points(circle, incident_ray_vector, density, distance, tol)
    else:
        start_points = [start_point]

    intersection_points = []
    reflection_lights = []
    refraction_lights = []

    incident_lines = []
    reflection_lines = []
    refraction_lines = []

    time_of_intersection = 1
    intersection_points_1 = [intersection(circle, incident_ray_vector, p)[0] \
                                for p in start_points]
    intersection_points.append(intersection_points_1)
    reflect_1 = [reflection(circle, incident_ray, intersection_point) \
                        for intersection_point in intersection_points_1]
    refract_1 =  [refraction(circle, incident_ray, intersection_point, refraction_index) \
                        for intersection_point in intersection_points_1]
    reflection_lights.append(reflect_1)
    refraction_lights.append(refract_1)

    incident_line_1 = [draw_linesegment(start_point, end_point, color=COLORS[0]) \
        for (start_point, end_point) in zip(start_points, intersection_points_1)]
    reflect_line_1 = [light_reflection_outside(circle, reflection_light, intersection_point, color=COLORS[0], times=distance) \
        for (reflection_light, intersection_point) in zip(reflect_1, intersection_points_1)]
    refract_line_1 = [light_intersection(circle, refraction_light, intersection_point, color=COLORS[0]) \
        for (refraction_light, intersection_point) in zip(refract_1, intersection_points_1)]
    incident_lines.append(incident_line_1)
    reflection_lines.append(reflect_line_1)
    refraction_lines.append(refract_line_1)


    if 1 == intersection_time:
        intersection_points = [(x, y) for p in intersection_points for (x, y) in p]
        intersection_points = tuple(zip(*intersection_points))
        points_and_lines = dict(incident_lines=incident_lines,
                            reflection_lines=reflection_lines,
                            refraction_lines=refraction_lines,
                            intersection_points=intersection_points)
        return points_and_lines

    incident_lights = refraction_lights[0]
    while time_of_intersection < intersection_time:
        color_offset = (-1)*time_of_intersection//2 - 1 if time_of_intersection%2 else time_of_intersection//2 
        intersect_points = [intersection(circle, incident_light.direction, start_p)[0] \
                                for (incident_light, start_p) in zip(incident_lights, intersection_points[time_of_intersection-1])]
        intersection_points.append(intersect_points)
        reflect_lights = [reflection(circle, incident_light, intersect_point) \
                                for (incident_light, intersect_point) in zip(incident_lights, intersect_points)]
        refract_lights = [refraction(circle, incident_light, intersect_point, outside_ref_index) \
                                for (incident_light, intersect_point) in zip(incident_lights, intersect_points)]

        reflect_lines = [light_intersection(circle, reflect_light, intersect_point, COLORS[color_offset]) \
                                for (reflect_light, intersect_point) in zip(reflect_lights, intersect_points)]
        refract_lines = [light_reflection_outside(circle, refract_light, intersect_point, COLORS[color_offset], distance) \
                                for (refract_light, intersect_point) in zip(refract_lights, intersect_points)]
        reflection_lines.append(reflect_lines)
        refraction_lines.append(refract_lines)

        incident_lights = reflect_lights
        time_of_intersection += 1

    intersection_points = [(x, y) for p in intersection_points for (x, y) in p]
    intersection_points = tuple(zip(*intersection_points))
    points_and_lines = dict(incident_lines=incident_lines, 
                            reflection_lines=reflection_lines,
                            refraction_lines=refraction_lines,
                            intersection_points=intersection_points)
    return points_and_lines



def main():
    radius = 1
    center = (0, 0)
    circle = Circle(radius, center)
    density = 10
    vector = Vec2d(1, 0).normalized()
    incident_light = Light(532, vector, 1, unit='nm')
    refraction_index = 1.335

    points_and_lines = drawer(circle, incident_light, density, refraction_index, intersection_time=2)
    xy = points_and_lines.pop('intersection_points')
    plot_lines = [line for l in points_and_lines.values() for ll in l for line in ll]

    fig, ax = plt.subplots(1, 1)
    fig = plt.scatter(xy[0], xy[1])
    circle_plot = plt.Circle(center, radius, fill=False)
    plt.gca().add_patch(circle_plot)

    for l in plot_lines:
        ax.add_line(l)

    plt.axis('equal')
    boarder = 3
    plt.axis([-boarder, boarder, -boarder, boarder])
    plt.show()


if __name__ == '__main__':
    main()