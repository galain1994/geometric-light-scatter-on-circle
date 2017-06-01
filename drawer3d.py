#/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import division
import math
import numpy as np
import matplotlib.pyplot as plt
from itertools import product
from copy import deepcopy
from mpl_toolkits.mplot3d import axes3d
from mpl_toolkits.mplot3d import art3d
from pygameVector import Vec3d
from funcs3d import *
from intersectionElements import Sphere, Light


COLORS = ['#FF0033', '#CC00CC', '#FF6600', '#33FF33',
          '#00FFFF', '#006666', '#000000', '#00ff7f',
          '#CCCCCC', '#e8b32d', '#8470ff', '#87cefa',
          '#20b2aa', '#f08080', '#ff6eb4', '#f0fff0',
          '#ff3030', '#1e90ff', '#00b2ee', '#97ffff',
          '#b23aee', '#98f5ff', '#8a2be2', '#00f5ff',
          '#00f5ff', '#8a6bee', '#ec0070', '#22e2c1',
          '#9e81d9', '#9202f5', '#01d9e1']


def generate_sphere_cordinates(radius, longitude, latitude):
    longitude = complex(0, longitude)
    latitude = complex(0, latitude)
    u, v = np.mgrid[0:2*np.pi:longitude, 0:np.pi:latitude]
    x = radius * np.cos(u)*np.sin(v)
    y = radius * np.sin(u)*np.sin(v)
    z = radius * np.cos(v)
    return (x, y, z)


def generate_skeleton(radius, horizon_or_vertical):
    theta = np.linspace(-np.pi, np.pi, 100)
    if 'h' == horizon_or_vertical:
        x = radius * np.sin(theta)
        y = radius * np.cos(theta)
        z = np.linspace(0, 0, 100)
    elif 'v' == horizon_or_vertical:
        z = radius * np.sin(theta)
        x = radius * np.cos(theta)
        y = np.linspace(0, 0, 100)
    else:
        y = radius * np.sin(theta)
        z = radius * np.cos(theta)
        x = np.linspace(0, 0, 100)
    return (x, y, z)


def generate_centerline(radius):
    vertical_line = draw_line((0, 0, -radius), (0, 0, radius), ':', 'b', 0.5)
    horizon_line = draw_line((-radius, 0, 0), (radius, 0, 0), ':', 'b', 0.5)
    plain_line = draw_line((0, -radius, 0), (0, radius, 0), ':', 'b', 0.5)
    return [vertical_line, horizon_line, plain_line]


def draw_sphere_at_axes(ax, radius, longitude, latitude, linewidth, color, alpha=0.1):

    x, y, z = generate_sphere_cordinates(radius, longitude, latitude)
    ax.plot_surface(x, y, z, color=color, alpha=alpha)             # 画出表面
    horizon_skeleton, vertical_skeleton, plain_skeleton = generate_skeleton(radius, 'h'),\
                                                          generate_skeleton(radius, 'v'),\
                                                          generate_skeleton(radius, 'p')    # 球内部的圆
    skeletons = [horizon_skeleton, vertical_skeleton, plain_skeleton]
    for skeleton in skeletons:
        ax.plot(*skeleton, ':', linewidth=linewidth, color=color)
    for line in generate_centerline(radius):
        ax.add_line(line)

    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')
    return ax


def draw_line(s, e, linestyle='dashed', color='b', linewidth=1.5, label=None):
    l = art3d.Line3D((s[0], e[0]), (s[1], e[1]), (s[2], e[2]), color=color, linewidth=linewidth, label=label)
    x_data = np.ndarray(shape=(1, 2), buffer=np.array([float(s[0]), float(e[0])]), dtype=np.float64)
    y_data = np.ndarray(shape=(1, 2), buffer=np.array([float(s[1]), float(e[1])]), dtype=np.float64)
    z_data = np.ndarray(shape=(1, 2), buffer=np.array([float(s[2]), float(e[2])]), dtype=np.float64)
    setattr(l, '_x', x_data)
    setattr(l, '_y', y_data)
    setattr(l, '_z', z_data)
    l.set_linestyle(linestyle)
    return l


def draw_line_outside(start, vector, length, linestyle='dashed', color='b', linewidth=1.5, label=None):
    s = start
    vector = vector.normalized() * length
    e = start + vector
    return draw_line(s, e, linestyle, color, linewidth, label)


def drawer(sphere, incident_light, refraction_index, start_point, intersection_time=1):

    radius = sphere.radius

    points = []
    lines = []

    time_of_intersection = 1
    color_offset = 2
    points.append(start_point)
    first_intersection_point = calculate_intersection_on_sphere(sphere, incident_light, start_point)[0]
    points.append(first_intersection_point)
    lines.append(draw_line(start_point, first_intersection_point, 'solid', COLORS[0]))
    lines[0].set_label('N%s' % time_of_intersection)

    factor = ref_factors(sphere, incident_light, first_intersection_point)
    reflection_light = reflection(factor, incident_light)
    refraction_light = refraction(factor, incident_light, refraction_index)

    first_reflection_line = draw_line_outside(first_intersection_point, reflection_light.direction, 2*radius, 'solid', COLORS[color_offset])
    second_intersection_point = calculate_intersection_on_sphere(sphere, refraction_light, first_intersection_point)[0]
    points.append(second_intersection_point)
    first_refraction_line = draw_line(first_intersection_point, second_intersection_point, color=COLORS[1])
    lines.append(first_reflection_line)
    lines.append(first_refraction_line)

    if 1 == intersection_time:
        return dict(points=points,
                    lines=lines)
    else:
        incident_light = refraction_light
        intersection_point = second_intersection_point
        while time_of_intersection < intersection_time:
            time_of_intersection += 1
            color_offset = color_offset+1
            factor = ref_factors(sphere, incident_light, intersection_point)
            reflection_light = reflection(factor, incident_light)
            refraction_light = refraction(factor, incident_light, 1)

            refraction_line = draw_line_outside(intersection_point, refraction_light.direction, 2*radius, 'solid', color=COLORS[color_offset])
            refraction_line.set_label('N%s' % time_of_intersection)
            next_intersection_point = calculate_intersection_on_sphere(sphere, reflection_light, intersection_point)[0]
            points.append(next_intersection_point)
            reflection_line = draw_line(intersection_point, next_intersection_point, color=COLORS[1])
            lines.append(reflection_line)
            lines.append(refraction_line)
            incident_light = reflection_light
            intersection_point = next_intersection_point
        return dict(points=points,
                    lines=lines)


def generate_multi_start_points(radius, num, set_x=None, set_y=None, set_z=None):
    # 绘制片状光与面状光
    def combine(iterable, _set):
        for i in iterable:
            yield (i, _set)

    coordinates = [[], [], []]   # 初始化三个坐标容器
    x, y, z = [], [], []
    step = 2*radius/(num-1)
    scope = [-radius+step*i for i in range(num)]
    for i, _setting in enumerate((set_x, set_y, set_z)):
        if _setting is None:
            _co = deepcopy(scope)
        else:
            _co = [_setting]
        coordinates[i] = _co
    start_point_list = list(product(coordinates[0], coordinates[1], coordinates[2]))
    return start_point_list


def multi_line_drawer(sphere, incident_light, refraction_index, start_point_list, intersection_time):
    # 绘制多个起点的散射情况
    radius = sphere.radius
    
    points = []
    reflection_lines = []
    refraction_lines = []
    incident_lines = []
    refraction_lights_main = []
    reflection_lights_main = []
    lines = {'refraction_lines': refraction_lines,
             'reflection_lines': reflection_lines,
             'incident_lines': incident_lines}
    lights = {'refraction_lights': refraction_lights_main,
              'reflection_lights': reflection_lights_main}

    points.append(start_point_list)
    time_of_intersection = 1
    color_offset = 2
    # 第一次作用
    first_intersection_point_list = [calculate_intersection_on_sphere(sphere, incident_light, p) for p in start_point_list]
    incident_line = [draw_line(s, e[0], 'solid', COLORS[0]) for (s, e) in zip(start_point_list, first_intersection_point_list) if e]
    lines['incident_lines'].append(incident_line)

    first_intersection_point_list = [p[0] for p in first_intersection_point_list if p] # 清除无效点
    points.append(first_intersection_point_list)

    factors_list = [ref_factors(sphere, incident_light, p) for p in first_intersection_point_list]
    first_reflection_lights = [reflection(factor, incident_light) for factor in factors_list]
    reflection_lights_main.append(first_reflection_lights)
    first_refraction_lights = [refraction(factor, incident_light, refraction_index) for factor in factors_list]
    refraction_lights_main.append(first_refraction_lights)

    first_reflection_lines = [draw_line_outside(s, light.direction, 2*radius, 'solid', COLORS[color_offset])
                                for (light, s) in zip(first_reflection_lights, first_intersection_point_list)]
    first_reflection_lines[0].set_label('N1')
    # [0] 指(end, start) 是与球的第二个交点end, 起点是start
    second_intersection_point_list = [calculate_intersection_on_sphere(sphere, light, p)[0] 
                                for (light, p) in zip(first_refraction_lights, first_intersection_point_list)]
    first_refraction_lines = [draw_line(s, e, color=COLORS[1]) for (s, e) in zip(first_intersection_point_list, second_intersection_point_list)]

    reflection_lines.append(first_reflection_lines)
    refraction_lines.append(first_refraction_lines)


    if 1 < intersection_time:
        # 作用次数大于1
        incident_lights = first_refraction_lights
        intersection_point_list = second_intersection_point_list
        while time_of_intersection < intersection_time:
            time_of_intersection += 1
            # 选择颜色
            color_offset = color_offset+1
            # 球内反射光
            factors_list = [ref_factors(sphere, light, p) for (light, p) in zip(incident_lights, intersection_point_list)]
            reflection_lights = [reflection(factor, light) 
                                    for (factor, light) in zip(factors_list, incident_lights)]
            reflection_lights_main.append(reflection_lights)
            # 折射光，出射
            refraction_lights = [refraction(factor, light, 1)
                                    for (factor, light) in zip(factors_list, incident_lights)]
            refraction_lights_main.append(refraction_lights)

            # 折射 出射线段
            refraction_lines = [draw_line_outside(s, light.direction, 2*radius, 'solid', COLORS[color_offset])
                                    for (light, s) in zip(refraction_lights, intersection_point_list)]
            refraction_lines[0].set_label('N%s' % time_of_intersection)
            lines['refraction_lines'].append(refraction_lines)

            # 作用点（下次）
            next_intersection_point_list = [calculate_intersection_on_sphere(sphere, light, p)[0]
                                                for (light, p) in zip(reflection_lights, intersection_point_list)]
            points.append(next_intersection_point_list)
            # 反射光线段
            reflection_lines = [draw_line(s, e, color=COLORS[1]) for (s, e) in zip(intersection_point_list, next_intersection_point_list)]
            lines['reflection_lines'].append(reflection_lines)
            incident_lights = reflection_lights
            intersection_point_list = next_intersection_point_list
    points = [(x, y, z) for times_points in points for (x, y, z) in times_points]
    points = tuple(zip(*points))
    return dict(points=points,
                lines=lines,
                lights=lights)




def main():

    radius = 10
    sphere = Sphere(radius, (0, 0, 0))

    v = Vec3d(0, 1, 0)
    light = Light(532, v, 1, unit='nm')
    refraction_index = 1.335

    set_z = 0
    density = 2000
    start_point_list1 = generate_multi_start_points(radius, density, set_y=-15, set_z=set_z)
    # start_point_list2 = generate_multi_start_points(radius, 5, set_y=-15)

    intersection_time = 4
    points_and_lines_and_lights = multi_line_drawer(sphere, light, refraction_index, start_point_list1, intersection_time)
    points = points_and_lines_and_lights['points']


    lights = points_and_lines_and_lights['lights']['refraction_lights']
    lights[0] = points_and_lines_and_lights['lights']['reflection_lights'][0]

    x = []
    y = []
    annotate_x = []
    annotate_y = []
    import matplotlib.pyplot as plt
    for l in lights:
        x.append(list(range(len(l))))
        anno_x = [0, len(l)//2, len(l)-1]
        annotate_x.append(anno_x)
        elevation_angle = [ calculate_elevation_angle(light.direction) for light in l]
        # y.append(elevation_angle)  # 抬升角
        # annotate_y.append([elevation_angle[anno_x[0]], 
        #                    elevation_angle[anno_x[1]], 
        #                    elevation_angle[anno_x[2]]])
        azimuth = [ math.degrees(math.atan2(light.direction.x, light.direction.y)) for light in l]
        y.append(azimuth) # 方位角

    for l in lights[2]:
        print (l.direction.x, l.direction.y, l.direction.z)


    fig, axes = plt.subplots(2, 2)
    axes[0][0].scatter(x[0], y[0])
    axes[0][0].set_title('N=1')
    axes[0][1].scatter(x[1], y[1])
    axes[0][1].set_title('N=2')
    axes[1][0].scatter(x[2], y[2])
    axes[1][0].set_title('N=3')
    axes[1][1].scatter(x[3], y[3])
    axes[1][1].set_title('N=4')

    # offset = 0
    # for row_axes in axes:
    #     for ax in row_axes:
    #         for anno_x, anno_y in zip(annotate_x[offset], annotate_y[offset]):
    #             ax.annotate("%i, %s°" % (int(anno_x), str(round(anno_y, 2))), (anno_x, anno_y))
    #         offset += 1
    
        
    for ax in axes[1]:
        ax.set_xlabel('x')
    for col, ax in enumerate(axes[0]):
        ax.axis(sharex=axes[1][col])
    # axes[0][0].set_ylabel('Elevation angle')
    axes[0][0].set_ylabel('azimuth angle')
    # axes[1][0].set_ylabel('Elevation angle')
    axes[1][0].set_ylabel('azimuth angle')
    for row, ax in enumerate(axes):
        for col, row_ax in enumerate(ax):
            row_ax.axis(sharey=axes[row][0])
    # plt.suptitle('Elevation angle (Z=%s)' % set_z)
    plt.suptitle('Azimuth angle (Z=%s)' % set_z)
    plt.show()


    # lines = points_and_lines_and_lights['lines'].values()
    # lines = [p_line for type_lines in lines for time_lines in type_lines for p_line in time_lines]


    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')
    # ax.scatter(*points)

    # for line in lines:
    #     ax.add_line(line)

    # x, y, z = generate_sphere_cordinates(radius, 100, 100)
    # alpha = 0.1
    # ax.plot_surface(x, y, z, color='b', alpha=alpha)
    # horizon_skeleton = generate_skeleton(radius, 'h')
    # vertical_skeleton = generate_skeleton(radius, 'v')
    # plain_skeleton = generate_skeleton(radius, 'p')
    # ax.plot(*horizon_skeleton, ':',  linewidth=0.8, color='b')
    # ax.plot(*vertical_skeleton, ':',  linewidth=0.8, color='b')
    # ax.plot(*plain_skeleton, ':',  linewidth=0.8, color='b')
    # for line in generate_centerline(radius):
    #     ax.add_line(line)
    # ax.set_xlabel('X Label')
    # ax.set_ylabel('Y Label')
    # ax.set_zlabel('Z Label')
    # ax.legend(loc='upper left', frameon=False)
    # plt.show()


if __name__ == '__main__':
    main()
    

