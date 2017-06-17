#/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import division
import matplotlib.pyplot as plt
from matplotlib import lines
from pygameVector import Vec2d
from intersectionElements import Circle, Light
from intersectionFuncs import intersection, reflection, refraction, pick_start_points, ref_factors


# 光线的颜色取值
COLORS = ['#FF0033', '#FF6600', '#FFFF33', '#33FF33',
          '#00FFFF', '#006666', '#CC00CC', '#000000',
          '#CCCCCC', '#e8b32d', '#8470ff', '#87cefa',
          '#20b2aa', '#f08080', '#ff6eb4', '#f0fff0',
          '#ff3030', '#1e90ff', '#00b2ee', '#97ffff',
          '#b23aee', '#98f5ff', '#8a2be2', '#00f5ff',
          '#00f5ff', '#8a6bee', '#ec0070', '#22e2c1',
          '#9e81d9', '#9202f5', '#01d9e1', '#00ff7f']


def draw_linesegment(start_point, end_point, color):
    """draw line from to point coordinates
    画直线片段。传入起点坐标，终点坐标，颜色。
    颜色可以是十六进制，可以是颜色简写
    """
    x = (start_point[0], end_point[0])
    y = (start_point[1], end_point[1])
    line = lines.Line2D(x, y, color=color)
    return line


def light_reflection_outside(circle, light, start_point, color='b', times=2):
    """outside the circle; the reflection 画圆外的反射的光线
    @circle: Circle的实例
    @light:  Light的实例
    @start_point: 起始点
    @color
    @times: 长度是半径几倍
    """
    vector = light.direction
    vectortimes = vector.normalized() * circle.radius * times
    end_point = (start_point[0] + vectortimes.x, start_point[1] + vectortimes.y)
    line = draw_linesegment(start_point, end_point, color)
    return line


def light_intersection(circle, light, start_point, color='b'):
    """draw from Light class 画在圆内传播的光线的线段
    """
    vector = light.direction
    intersection_point = intersection(circle, light.direction, start_point) # 计算交点
    end_point = intersection_point[0] # 取交点中的终点
    line = draw_linesegment(start_point, end_point, color)
    return line


def drawer(circle, incident_light, refraction_index, density=1, outside_ref_index=1, intersection_time=1, distance=2, tol=1e-2, start_point=None):
    """根据给定的条件，画追迹光线的主程序
    @param:circle Circle的实例
    @param:incident_light 入射光
    @param:refraction_index 圆柱内折射率
    @param:density 光线条数
    @param:outside_ref_index 外界折射率 默认为真空 为1
    @param:intersection_time 作用次数，最少一次  how many time the light intersect the circle
    @param:distance 画圆外的光线时，长度为半径的几倍             how many times of line expand multiply by the radius
    @param:tol 光线离圆顶端的距离默认是0.01                  the distance to the boarder of the circle
    @param:start_point 给定的起始点，可以是列表，可以是单个点，默认是None，则自动生成
    RETURN 字典 交点，光线与线段的结果
    """
    if not isinstance(intersection_time, int) or intersection_time < 1:
        raise ValueError('Intersection times should not be less than 1 and should be int') # 作用次数不能小于1，作用次数为整数

    radius = circle.radius
    center = circle.center
    incident_light_vector = incident_light.direction.normalized()  # 入射光方向的单位化

    if not start_point:
        start_points = pick_start_points(circle, incident_light_vector, density, distance, tol)
    else:
        start_points = start_point if isinstance(start_point, list) else [start_point] # 转化为列表

    intersection_points = [] # 交点列表
    reflection_lights = []  # 反射光线
    refraction_lights = []  # 折射光线

    incident_lines = [] # 入射光线
    reflection_lines = [] # 反射线段
    refraction_lines = [] # 折射线段

    time_of_intersection = 1
    # 第一次作用的交点 若没有交点则舍弃
    intersection_points_1 = [intersection(circle, incident_light_vector, p)[0] for p in start_points if intersection(circle, incident_light_vector, p)]
    intersection_points.append(intersection_points_1)

    factors_list = [ref_factors(circle, incident_light, p) for p in intersection_points_1]  # 第一次作用的边界条件计算的到中间变量
    reflect_1 = [reflection(factor, incident_light) \
                        for factor in factors_list]
    refract_1 =  [refraction(factor, incident_light, refraction_index) \
                        for factor in factors_list]
    reflection_lights.append(reflect_1)
    refraction_lights.append(refract_1)

    # 入射光线的线段
    incident_line_1 = [draw_linesegment(start_point, end_point, color=COLORS[0]) \
        for (start_point, end_point) in zip(start_points, intersection_points_1)]
    # 反射光线的线段
    reflect_line_1 = [light_reflection_outside(circle, reflection_light, intersection_point, color=COLORS[-1], times=distance) \
        for (reflection_light, intersection_point) in zip(reflect_1, intersection_points_1)]
    # 折射光线的线段
    refract_line_1 = [light_intersection(circle, refraction_light, intersection_point, color=COLORS[-1]) \
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
                            intersection_points=intersection_points,
                            reflection_lights=reflection_lights,
                            refraction_lights=refraction_lights)
        return points_and_lines

    incident_lights = refraction_lights[0]
    # 循环到输入的作用的次数
    while time_of_intersection < intersection_time:
        time_of_intersection += 1
        # 选取颜色偏移量 参照COLORS全局变量
        color_offset = (-1)*(time_of_intersection+1)//2 - 1 if (time_of_intersection+1)%2 else (time_of_intersection+1)//2 
        intersect_points = [intersection(circle, incident_light.direction, start_p)[0] \
                                for (incident_light, start_p) in zip(incident_lights, intersection_points[time_of_intersection-2])]
        intersection_points.append(intersect_points)

        factors_list = [ref_factors(circle, incident_light, p) for (incident_light, p) in zip(incident_lights, intersect_points)]
        reflect_lights = [reflection(factor, incident_light) \
                                for (factor, incident_light) in zip(factors_list, incident_lights)]
        refract_lights = [refraction(factor, incident_light, outside_ref_index) \
                                for (factor, incident_light) in zip(factors_list, incident_lights)]
        reflection_lights.append(reflect_lights)
        refraction_lights.append(refract_lights)

        reflect_lines = [light_intersection(circle, reflect_light, intersect_point, COLORS[color_offset]) \
                                for (reflect_light, intersect_point) in zip(reflect_lights, intersect_points)]
        refract_lines = [light_reflection_outside(circle, refract_light, intersect_point, COLORS[color_offset], distance) \
                                for (refract_light, intersect_point) in zip(refract_lights, intersect_points)]
        reflection_lines.append(reflect_lines)
        refraction_lines.append(refract_lines)

        incident_lights = reflect_lights

    intersection_points = [(x, y) for p in intersection_points for (x, y) in p] # 解构交点
    intersection_points = tuple(zip(*intersection_points))   # 转化为x，y的两个列表
    points_and_lines = dict(incident_lines=incident_lines, 
                            reflection_lines=reflection_lines,
                            refraction_lines=refraction_lines,
                            intersection_points=intersection_points,
                            reflection_lights=reflection_lights,
                            refraction_lights=refraction_lights)
    return points_and_lines



def main():
    # 画出汇总图（essay）的script
    import math

    radius = 10
    center = (0, 0)
    circle = Circle(radius, center)
    density = 2000
    vector = Vec2d(1, 0).normalized()
    incident_light = Light(532, vector, 1, unit='nm')
    refraction_index = 1.335

    points_and_lines = drawer(circle, incident_light, refraction_index, density, intersection_time=8)
    xy = points_and_lines.pop('intersection_points')

    lights = points_and_lines['refraction_lights']
    lights[0] = points_and_lines['reflection_lights'][0]
    x = list(range(len(lights[0])))
    y = []
    for l in lights:
        y.append([light.direction.angle for light in l])

    # 画出论文所需的方位角的图
    fig, axes = plt.subplots(2, 4)
    s = [5] * len(x) # size of the point
    axes[0][0].scatter(x, y[0], s=s)
    axes[0][1].scatter(x, y[1], s=s)
    axes[0][2].scatter(x, y[2], s=s)
    axes[0][3].scatter(x, y[3], s=s)
    axes[1][0].scatter(x, y[4], s=s)
    axes[1][1].scatter(x, y[5], s=s)
    axes[1][2].scatter(x, y[6], s=s)
    axes[1][3].scatter(x, y[7], s=s)
    for i, a in enumerate([ i for j in axes for i in j]):
        a.set_title('N = %s' % str(i+1))
    plt.show()


if __name__ == '__main__':
    main()