#/usr/bin/env python
# -*- coding:utf-8 -*-

import math
from numpy import matrix
from pygameVector import Vec3d
from intersectionElements import Light, Sphere

__all__ = [ 'calculate_elevation_angle','generate_start_points', 'calculate_intersection_on_sphere',
            'reflection', 'refraction', 'ref_factors']


def calculate_elevation_angle(vector):
    kx, ky, kz = vector
    return math.degrees(math.atan2(kz, math.sqrt(kx*kx+ky*ky)))


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


def calculate_intersection_on_sphere(sphere, light, start):
    # 用与光线与球交点的求解
    v = light.direction
    center_vector = Vec3d(sphere.center)
    radius = sphere.radius
    if Vec3d(0, 0, 0) == v:
        return None
    if sphere.on_sphere(start):
        # 起点在球上，则顺序为（另一点， 起点）
        t = (-2) * (v.x*start[0] + v.y*start[1] + v.z*start[2]) / (v.x**2+v.y**2+v.z**2)
        end = start + t*v
        return (end, start)
    else:
        # 起点不在球上，顺序为（离起点较近的点， 离起点较远的点）
        # 与球没有交点，则返回None
        a = v.dot(v)
        b = 2*v.dot(start-center_vector)
        c = (start-center_vector).dot(start-center_vector) - radius*radius
        disc = b*b - 4*a*c
        if disc<0:
            return None
        sqrt_disc = math.sqrt(disc)
        t1 = (-b - sqrt_disc) / (2*a)
        t2 = (-b + sqrt_disc) / (2*a)
        return (start+t1*v, start+t2*v)
        

def ref_factors(sphere, light, intersection_point):
    center = sphere.center
    radius = sphere.radius

    k_li_vector = light.k_vector

    # vector on the surface of the intersection
    unit_n_vector = Vec3d(tuple((intersection_point[i]-center[i])/radius for i in range(3))).normalized()
    unit_b_vector = (light.direction.cross(unit_n_vector)).normalized()
    unit_t_vector = (unit_b_vector.cross(unit_n_vector)).normalized()
    c = matrix([unit_n_vector, unit_t_vector, unit_b_vector]).T

    k_normal = k_li_vector.dot(unit_n_vector)
    k_tangen = k_li_vector.dot(unit_t_vector)

    return dict(c=c, tangen=k_tangen, normal=k_normal)


def reflection(factors, light):
    wavelength = light.wavelength
    refraction_index = light.refraction_index

    # light factor 
    normal = (-1) * factors['normal']
    tangen = factors['tangen']
    c = factors['c']

    # reflection light vector
    direction = c * matrix([[normal], [tangen], [0]])
    direction = Vec3d(direction.A1).normalized()
    return Light(wavelength, direction, refraction_index)


def refraction(factors, light, refraction_index):
    wavelength = light.wavelength
    k = Light.wavenum(wavelength, refraction_index)

    normal_sgn = 1 if factors['normal'] > 0 else -1
    tangen = factors['tangen']
    normal = normal_sgn * math.sqrt(k*k-tangen*tangen)
    c = factors['c']

    direction = (c*matrix([[normal], [tangen], [0]])).A1
    direction = Vec3d(direction).normalized()
    return Light(wavelength, direction, refraction_index)











