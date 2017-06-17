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

# 光线颜色的取值
COLORS = ['#FF0033', '#CC00CC', '#FF6600', '#33FF33',
          '#00FFFF', '#006666', '#000000', '#00ff7f',
          '#CCCCCC', '#e8b32d', '#8470ff', '#87cefa',
          '#20b2aa', '#f08080', '#ff6eb4', '#f0fff0',
          '#ff3030', '#1e90ff', '#00b2ee', '#97ffff',
          '#b23aee', '#98f5ff', '#8a2be2', '#00f5ff',
          '#00f5ff', '#8a6bee', '#ec0070', '#22e2c1',
          '#9e81d9', '#9202f5', '#01d9e1']


def generate_sphere_cordinates(radius, longitude, latitude):
    """生成球的表面坐标
    """
    longitude = complex(0, longitude)
    latitude = complex(0, latitude)
    u, v = np.mgrid[0:2*np.pi:longitude, 0:np.pi:latitude]
    x = radius * np.cos(u)*np.sin(v)
    y = radius * np.sin(u)*np.sin(v)
    z = radius * np.cos(v)
    return (x, y, z)


def generate_skeleton(radius, horizon_or_vertical):
    """生成球子午线，赤道线等圆
    horizon_or_vertical: 竖直圆，水平圆，直面照射的圆形
    """
    theta = np.linspace(-np.pi, np.pi, 100) # 角度
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
    """球中心十字的虚线（南北极，经过赤道的直径）
    """
    vertical_line = draw_line((0, 0, -radius), (0, 0, radius), ':', 'b', 0.5)
    horizon_line = draw_line((-radius, 0, 0), (radius, 0, 0), ':', 'b', 0.5)
    plain_line = draw_line((0, -radius, 0), (0, radius, 0), ':', 'b', 0.5)
    return [vertical_line, horizon_line, plain_line]


def draw_sphere_at_axes(ax, radius, longitude, latitude, linewidth, color, alpha=0.1):
    """将骨架添加到ax（子图）中
    """
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
    """画出3d的线段
    s: start point (x, y, z)
    e: end point (x, y, z)
    label: 标记与注记的设定 string
    """
    l = art3d.Line3D((s[0], e[0]), (s[1], e[1]), (s[2], e[2]), color=color, linewidth=linewidth, label=label)
    x_data = np.ndarray(shape=(1, 2), buffer=np.array([float(s[0]), float(e[0])]), dtype=np.float64)
    y_data = np.ndarray(shape=(1, 2), buffer=np.array([float(s[1]), float(e[1])]), dtype=np.float64)
    z_data = np.ndarray(shape=(1, 2), buffer=np.array([float(s[2]), float(e[2])]), dtype=np.float64)
    setattr(l, '_x', x_data)    # 将坐标值做为属性传入line
    setattr(l, '_y', y_data)
    setattr(l, '_z', z_data)
    l.set_linestyle(linestyle)
    return l


def draw_line_outside(start, vector, length, linestyle='dashed', color='b', linewidth=1.5, label=None):
    """画出球外界的线段
    """
    s = start
    vector = vector.normalized() * length
    e = start + vector
    return draw_line(s, e, linestyle, color, linewidth, label)


def drawer(sphere, incident_light, refraction_index, start_point, intersection_time=1):
    """单条光线的追迹主程序
    """
    if not isinstance(intersection_time, int) or intersection_time < 1:
        raise ValueError('Intersection times should not be less than 1 and should be int') # 作用次数不能小于1，作用次数为整数

    radius = sphere.radius

    points = []
    lines = []

    time_of_intersection = 1
    color_offset = 2
    points.append(start_point)
    try:
        first_intersection_point = calculate_intersection_on_sphere(sphere, incident_light, start_point)[0] # 计算第一次作用的交点
    except TypeError:
        return None
    points.append(first_intersection_point)
    lines.append(draw_line(start_point, first_intersection_point, 'solid', COLORS[0]))  # 第一种颜色
    lines[0].set_label('N%s' % time_of_intersection)    # 标记N1 为入射光线

    factor = ref_factors(sphere, incident_light, first_intersection_point) # 边界条件
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
            color_offset = color_offset+1 # 折射光颜色的偏移量
            factor = ref_factors(sphere, incident_light, intersection_point)
            reflection_light = reflection(factor, incident_light)   # 反射光
            refraction_light = refraction(factor, incident_light, 1)    # 折射光 外界折射率为1

            refraction_line = draw_line_outside(intersection_point, refraction_light.direction, 2*radius, 'solid', color=COLORS[color_offset])
            refraction_line.set_label('N%s' % time_of_intersection) # 折射光线段的标记
            next_intersection_point = calculate_intersection_on_sphere(sphere, reflection_light, intersection_point)[0] # 下一个作用点
            points.append(next_intersection_point)
            reflection_line = draw_line(intersection_point, next_intersection_point, color=COLORS[1])   # 反射光都用第二种颜色
            lines.append(reflection_line)
            lines.append(refraction_line)
            incident_light = reflection_light
            intersection_point = next_intersection_point  # 将下一个作用点作为起始点
        return dict(points=points,
                    lines=lines)


def generate_multi_start_points(radius, num, set_x=None, set_y=None, set_z=None):
    """绘制片状光与面状光 若设定某个坐标值不变，则其余的从（-r，r）取num个值，步长为2r/(num-1)
    @param:set_x 设定x不变的坐标值
    @param:set_y
    @param:set_z

    """
    def combine(iterable, _set):
        for i in iterable:
            yield (i, _set)

    coordinates = [[], [], []]   # 初始化三个坐标容器
    x, y, z = [], [], []
    step = 2*radius/(num-1)
    scope = [-radius+step*i for i in range(num)]    # 不设定的坐标值的取值范围
    for i, _setting in enumerate((set_x, set_y, set_z)):
        if _setting is None:
            _co = deepcopy(scope)
        else:
            _co = [_setting]
        coordinates[i] = _co
    start_point_list = list(product(coordinates[0], coordinates[1], coordinates[2]))
    return start_point_list


def multi_line_drawer(sphere, incident_light, refraction_index, start_point_list, intersection_time):
    """光簇的追迹的主程序
    """
    if not isinstance(intersection_time, int) or intersection_time < 1:
        raise ValueError('Intersection times should not be less than 1 and should be int') # 作用次数不能小于1，作用次数为整数

    radius = sphere.radius
    
    points = []
    reflection_lines = []
    refraction_lines = []
    incident_lines = []
    refraction_lights_main = [] # 所有折射光线的列表
    reflection_lights_main = [] # 所有反射光线的列表
    lines = {'refraction_lines': refraction_lines,
             'reflection_lines': reflection_lines,
             'incident_lines': incident_lines}
    lights = {'refraction_lights': refraction_lights_main,
              'reflection_lights': reflection_lights_main}

    points.append(start_point_list) # 将起始点加入到绘制点的列表中
    time_of_intersection = 1
    color_offset = 2
    # 第一次作用
    first_intersection_point_list = [calculate_intersection_on_sphere(sphere, incident_light, p) for p in start_point_list]
    incident_line = [draw_line(s, e[0], 'solid', COLORS[0]) for (s, e) in zip(start_point_list, first_intersection_point_list) if e]
    lines['incident_lines'].append(incident_line)

    first_intersection_point_list = [p[0] for p in first_intersection_point_list if p] # 过滤无作用点的起始点点
    if not first_intersection_point_list:   # 若过滤后无作用点 则返回 退出追迹
        return 
    points.append(first_intersection_point_list)

    factors_list = [ref_factors(sphere, incident_light, p) for p in first_intersection_point_list] # 交点处边界条件的参数的列表
    first_reflection_lights = [reflection(factor, incident_light) for factor in factors_list]
    reflection_lights_main.append(first_reflection_lights)
    first_refraction_lights = [refraction(factor, incident_light, refraction_index) for factor in factors_list]
    refraction_lights_main.append(first_refraction_lights)

    first_reflection_lines = [draw_line_outside(s, light.direction, 2*radius, 'solid', COLORS[color_offset])
                                for (light, s) in zip(first_reflection_lights, first_intersection_point_list)]
    first_reflection_lines[0].set_label('N1')
    # [0] (end, start)的第一项，第一项是指除去给定的起点以外的，与球两个交点中的另外一个交点
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
            # 折射光
            refraction_lights = [refraction(factor, light, 1)
                                    for (factor, light) in zip(factors_list, incident_lights)]
            refraction_lights_main.append(refraction_lights)

            # 折射光的线段 球外的线段
            refraction_lines = [draw_line_outside(s, light.direction, 2*radius, 'solid', COLORS[color_offset])
                                    for (light, s) in zip(refraction_lights, intersection_point_list)]
            refraction_lines[0].set_label('N%s' % time_of_intersection)
            lines['refraction_lines'].append(refraction_lines)

            # 下次作用点的坐标
            next_intersection_point_list = [calculate_intersection_on_sphere(sphere, light, p)[0]
                                                for (light, p) in zip(reflection_lights, intersection_point_list)]
            points.append(next_intersection_point_list)
            # 反射光线段 球内的线段
            reflection_lines = [draw_line(s, e, color=COLORS[1]) for (s, e) in zip(intersection_point_list, next_intersection_point_list)]
            lines['reflection_lines'].append(reflection_lines)
            incident_lights = reflection_lights
            intersection_point_list = next_intersection_point_list  # 将下次作用点的列表作为起始点的列表
    points = [(x, y, z) for times_points in points for (x, y, z) in times_points]   # 将作用点和起点转化为绘图所需的表示方式
    points = tuple(zip(*points))
    return dict(points=points,
                lines=lines,
                lights=lights)


def draw_azimuth_angle_distribution():
    """绘制论文所需方位角分布图
    """
    radius = 10
    sphere = Sphere(radius, (0, 0, 0))

    v = Vec3d(0, 1, 0)
    light = Light(532, v, 1, unit='nm')
    refraction_index = 1.335

    set_z = 0
    density = 100
    start_point_list1 = generate_multi_start_points(radius, density, set_y=-15, set_z=set_z)

    intersection_time = 4
    points_and_lines_and_lights = multi_line_drawer(sphere, light, refraction_index, start_point_list1, intersection_time)
    points = points_and_lines_and_lights['points']

    lights = points_and_lines_and_lights['lights']['refraction_lights']
    lights[0] = points_and_lines_and_lights['lights']['reflection_lights'][0]   # 第一次作用的光线选取反射光线

    x = []
    y = []
    annotate_x = [] # 标记的横坐标
    annotate_y = [] # 标记的纵坐标

    # 方位角
    for l in lights:
        x.append(list(range(len(l))))
        azimuth = [calculate_azimuth(light.direction) for light in l]
        y.append(azimuth) 
        anno_x = [0, len(l)//2, len(l)-1]
        annotate_x.append(anno_x)
        annotate_y.append([azimuth[anno_x[0]],
                           azimuth[anno_x[1]],
                           azimuth[anno_x[2]]])

    s = [5]*len(x) # 设置点的大小
    fig, axes = plt.subplots(2, 2)
    axes[0][0].scatter(x[0], y[0], s=s)
    axes[0][0].set_title('N=1')
    axes[0][1].scatter(x[1], y[1], s=s)
    axes[0][1].set_title('N=2')
    axes[1][0].scatter(x[2], y[2], s=s)
    axes[1][0].set_title('N=3')
    axes[1][1].scatter(x[3], y[3], s=s)
    axes[1][1].set_title('N=4')

    # 为图中的点设置标志
    offset = 0
    for row_axes in axes:
        for ax in row_axes:
            for anno_x, anno_y in zip(annotate_x[offset], annotate_y[offset]):
                ax.annotate("%i, %s°" % (int(anno_x), str(round(anno_y, 2))), (anno_x, anno_y)) # 设置点的标记（起点，中点，终点）
            offset += 1

    for ax in axes[1]:
        ax.set_xlabel('x')
    for col, ax in enumerate(axes[0]):  # 设置共享x坐标轴文字
        ax.axis(sharex=axes[1][col])
    axes[0][0].set_ylabel('Azimuth angle')  # 设置标题为方位角
    axes[1][0].set_ylabel('Azimuth angle')
    for row, ax in enumerate(axes):     # 设置共享y坐标轴文字
        for col, row_ax in enumerate(ax):
            row_ax.axis(sharey=axes[row][0])
    plt.show()


def draw_elevation_angle_distribution():
    """绘制论文所需抬升角分布图
    """
    radius = 10
    sphere = Sphere(radius, (0, 0, 0))

    v = Vec3d(0, 1, 0)
    light = Light(532, v, 1, unit='nm')
    refraction_index = 1.335

    set_z = 0
    density = 100
    start_point_list1 = generate_multi_start_points(radius, density, set_y=-15, set_z=set_z)    # 设定y轴坐标不变为-15， z轴不变味set_z

    intersection_time = 4
    points_and_lines_and_lights = multi_line_drawer(sphere, light, refraction_index, start_point_list1, intersection_time)
    points = points_and_lines_and_lights['points']

    lights = points_and_lines_and_lights['lights']['refraction_lights']
    lights[0] = points_and_lines_and_lights['lights']['reflection_lights'][0]   # 第一次作用的光线选取反射光线

    x = []
    y = []
    annotate_x = [] # 标记的横坐标
    annotate_y = [] # 标记的纵坐标

    # 抬升角
    for l in lights:
        x.append(list(range(len(l))))
        elevation_angle = [ calculate_elevation_angle(light.direction) for light in l]
        y.append(elevation_angle)  
        anno_x = [0, len(l)//2, len(l)-1]
        annotate_x.append(anno_x)
        annotate_y.append([elevation_angle[anno_x[0]], 
                           elevation_angle[anno_x[1]], 
                           elevation_angle[anno_x[2]]])


    s = [5]*len(x) # 设置点的大小
    fig, axes = plt.subplots(2, 2)  # 设置四个子图
    axes[0][0].scatter(x[0], y[0], s=s)
    axes[0][0].set_title('N=1')
    axes[0][1].scatter(x[1], y[1], s=s)
    axes[0][1].set_title('N=2')
    axes[1][0].scatter(x[2], y[2], s=s)
    axes[1][0].set_title('N=3')
    axes[1][1].scatter(x[3], y[3], s=s)
    axes[1][1].set_title('N=4')


    # 为图中的点设置标志
    offset = 0
    for row_axes in axes:
        for ax in row_axes:
            for anno_x, anno_y in zip(annotate_x[offset], annotate_y[offset]):
                ax.annotate("%i, %s°" % (int(anno_x), str(round(anno_y, 2))), (anno_x, anno_y)) # 设置点的标记（起点，中点，终点）
            offset += 1
    
        
    for ax in axes[1]:
        ax.set_xlabel('x')
    for col, ax in enumerate(axes[0]):  # 设置共享x坐标轴文字
        ax.axis(sharex=axes[1][col])
    axes[0][0].set_ylabel('Elevation angle')  # 标题 抬升角
    axes[1][0].set_ylabel('Elevation angle')
    for row, ax in enumerate(axes):     # 设置共享y坐标轴文字
        for col, row_ax in enumerate(ax):
            row_ax.axis(sharey=axes[row][0])
    plt.show()

    

