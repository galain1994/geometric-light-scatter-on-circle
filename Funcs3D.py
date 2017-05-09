#/usr/bin/env python
# -*- coding:utf-8 -*-

import math
from numpy import matrix
from pygameVector import Vec3d
from intersectionElements import Light, Sphere

__all__ = ['generate_start_points', 'calculate_first_intersection', 'calculate_intersection_on_sphere',
            'reflection', 'refraction']


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


def calculate_first_intersection(sphere, start_point):
    radius = sphere.radius
    center = sphere.center
    x = start_point[0] - center[0]
    z = start_point[2] - center[2]
    v = math.acos(z/radius)
    try:
        u = math.acos((x/(radius*math.sin(v)))) + math.pi
    except ValueError:
        return None
    else:
        intersection_y = radius * math.sin(u) * math.sin(v)
        return (x, intersection_y, z)


def calculate_intersection_on_sphere(sphere, light, start):
    v = light.direction
    center_vector = Vec3d(sphere.center)
    radius = sphere.radius
    if sphere.on_sphere(start):
        t = (-2) * (v.x*start[0] + v.y*start[1] + v.z*start[2]) / (v.x**2+v.y**2+v.z**2)
        end = start + t*v
        return (end, start)
    else:
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
        

def compution_on_intersection(sphere, light, intersection_point):
    center = sphere.center
    radius = sphere.radius

    k_li_vector = light.k_vector

    # vector on the surface of the intersection
    unit_n_vector = Vec3d(tuple((intersection_point[i]-center[i])/radius for i in range(3))).normalized()
    unit_b_vector = light.direction.cross(unit_n_vector)
    unit_t_vector = unit_b_vector.cross(unit_n_vector)
    c = matrix([unit_n_vector, unit_t_vector, unit_b_vector]).T

    k_normal = k_li_vector.dot(unit_n_vector)
    k_tangen = k_li_vector.dot(unit_t_vector)

    return dict(c=c, tangen=k_tangen, normal=k_tangen)


def reflection(sphere, light, intersection_point):
    wavelength = light.wavelength
    refraction_index = light.refraction_index

    factors = compution_on_intersection(sphere, light, intersection_point)

    # light factor 
    normal = (-1) * factors['normal']
    tangen = factors['tangen']
    c = factors['c']

    # reflection light vector
    direction = c * matrix([[normal], [tangen], [0]])
    direction = Vec3d(direction.A1)
    return Light(wavelength, direction, refraction_index)


def refraction(sphere, light, intersection_point, refraction_index):
    wavelength = light.wavelength
    k = Light.wavenum(wavelength, refraction_index)
    print (light.k)
    print (k)

    factors = compution_on_intersection(sphere, light, intersection_point)

    normal_sgn = 1 if factors['normal'] > 0 else -1
    normal = normal_sgn * math.sqrt(pow(k, 2) - pow(factors['tangen'], 2))
    tangen = factors['tangen']
    c = factors['c']

    direction = Vec3d((c*matrix([[normal], [tangen], [0]])).A1)
    return Light(wavelength, direction, refraction_index)


def main():
    radius = 10
    sphere = Sphere(radius)
    v = Vec3d(1, 0, 0)
    light = Light(532, v, 1)
    refraction_index = 1.335

    start_point = (0, -15, 6)
    intersection_point = calculate_first_intersection(start_point, radius)

    ref_light = reflection(sphere, light, intersection_point)
    refra_light = refraction(sphere, light, intersection_point, 1.335)
    
    intersection_points =  calculate_intersection_on_sphere(sphere, refra_light, intersection_point)
    print (intersection_point)
    print (intersection_points)

if __name__ == '__main__':
    main()











