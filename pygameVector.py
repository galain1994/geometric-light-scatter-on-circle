#/usr/bin/env python
# -*- coding=utf-8 -*-
################## http://www.pygame.org/wiki/2DVectorClass ##################
import operator
import math

class Vec2d(object):
    """2d vector class, supports vector and scalar operators,
       and also provides a bunch of high level functions
       """
    __slots__ = ['x', 'y']

    def __init__(self, x_or_pair, y = None):
        if y == None:
            self.x = x_or_pair[0]
            self.y = x_or_pair[1]
        else:
            self.x = x_or_pair
            self.y = y

    def __len__(self):
        return 2

    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        else:
            raise IndexError("Invalid subscript "+str(key)+" to Vec2d")

    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        else:
            raise IndexError("Invalid subscript "+str(key)+" to Vec2d")

    # String representaion (for debugging)
    def __repr__(self):
        return 'Vec2d(%s, %s)' % (self.x, self.y)

    # Comparison
    def __eq__(self, other):
        if hasattr(other, "__getitem__") and len(other) == 2:
            return self.x == other[0] and self.y == other[1]
        else:
            return False

    def __ne__(self, other):
        if hasattr(other, "__getitem__") and len(other) == 2:
            return self.x != other[0] or self.y != other[1]
        else:
            return True

    def __nonzero__(self):
        return bool(self.x or self.y)

    # Generic operator handlers
    def _o2(self, other, f):
        "Any two-operator operation where the left operand is a Vec2d"
        if isinstance(other, Vec2d):
            return Vec2d(f(self.x, other.x),
                         f(self.y, other.y))
        elif (hasattr(other, "__getitem__")):
            return Vec2d(f(self.x, other[0]),
                         f(self.y, other[1]))
        else:
            return Vec2d(f(self.x, other),
                         f(self.y, other))

    def _r_o2(self, other, f):
        "Any two-operator operation where the right operand is a Vec2d"
        if (hasattr(other, "__getitem__")):
            return Vec2d(f(other[0], self.x),
                         f(other[1], self.y))
        else:
            return Vec2d(f(other, self.x),
                         f(other, self.y))

    def _io(self, other, f):
        "inplace operator"
        if (hasattr(other, "__getitem__")):
            self.x = f(self.x, other[0])
            self.y = f(self.y, other[1])
        else:
            self.x = f(self.x, other)
            self.y = f(self.y, other)
        return self

    # Addition
    def __add__(self, other):
        if isinstance(other, Vec2d):
            return Vec2d(self.x + other.x, self.y + other.y)
        elif hasattr(other, "__getitem__"):
            return Vec2d(self.x + other[0], self.y + other[1])
        else:
            return Vec2d(self.x + other, self.y + other)
    __radd__ = __add__

    def __iadd__(self, other):
        if isinstance(other, Vec2d):
            self.x += other.x
            self.y += other.y
        elif hasattr(other, "__getitem__"):
            self.x += other[0]
            self.y += other[1]
        else:
            self.x += other
            self.y += other
        return self

    # Subtraction
    def __sub__(self, other):
        if isinstance(other, Vec2d):
            return Vec2d(self.x - other.x, self.y - other.y)
        elif (hasattr(other, "__getitem__")):
            return Vec2d(self.x - other[0], self.y - other[1])
        else:
            return Vec2d(self.x - other, self.y - other)
    def __rsub__(self, other):
        if isinstance(other, Vec2d):
            return Vec2d(other.x - self.x, other.y - self.y)
        if (hasattr(other, "__getitem__")):
            return Vec2d(other[0] - self.x, other[1] - self.y)
        else:
            return Vec2d(other - self.x, other - self.y)
    def __isub__(self, other):
        if isinstance(other, Vec2d):
            self.x -= other.x
            self.y -= other.y
        elif (hasattr(other, "__getitem__")):
            self.x -= other[0]
            self.y -= other[1]
        else:
            self.x -= other
            self.y -= other
        return self

    # Multiplication
    def __mul__(self, other):
        if isinstance(other, Vec2d):
            return Vec2d(self.x*other.x, self.y*other.y)
        if (hasattr(other, "__getitem__")):
            return Vec2d(self.x*other[0], self.y*other[1])
        else:
            return Vec2d(self.x*other, self.y*other)
    __rmul__ = __mul__

    def __imul__(self, other):
        if isinstance(other, Vec2d):
            self.x *= other.x
            self.y *= other.y
        elif (hasattr(other, "__getitem__")):
            self.x *= other[0]
            self.y *= other[1]
        else:
            self.x *= other
            self.y *= other
        return self

    # Division
    def __div__(self, other):
        return self._o2(other, operator.div)
    def __rdiv__(self, other):
        return self._r_o2(other, operator.div)
    def __idiv__(self, other):
        return self._io(other, operator.div)

    def __floordiv__(self, other):
        return self._o2(other, operator.floordiv)
    def __rfloordiv__(self, other):
        return self._r_o2(other, operator.floordiv)
    def __ifloordiv__(self, other):
        return self._io(other, operator.floordiv)

    def __truediv__(self, other):
        return self._o2(other, operator.truediv)
    def __rtruediv__(self, other):
        return self._r_o2(other, operator.truediv)
    def __itruediv__(self, other):
        return self._io(other, operator.floordiv)

    # Modulo
    def __mod__(self, other):
        return self._o2(other, operator.mod)
    def __rmod__(self, other):
        return self._r_o2(other, operator.mod)

    def __divmod__(self, other):
        return self._o2(other, operator.divmod)
    def __rdivmod__(self, other):
        return self._r_o2(other, operator.divmod)

    # Exponentation
    def __pow__(self, other):
        return self._o2(other, operator.pow)
    def __rpow__(self, other):
        return self._r_o2(other, operator.pow)

    # Bitwise operators
    def __lshift__(self, other):
        return self._o2(other, operator.lshift)
    def __rlshift__(self, other):
        return self._r_o2(other, operator.lshift)

    def __rshift__(self, other):
        return self._o2(other, operator.rshift)
    def __rrshift__(self, other):
        return self._r_o2(other, operator.rshift)

    def __and__(self, other):
        return self._o2(other, operator.and_)
    __rand__ = __and__

    def __or__(self, other):
        return self._o2(other, operator.or_)
    __ror__ = __or__

    def __xor__(self, other):
        return self._o2(other, operator.xor)
    __rxor__ = __xor__

    # Unary operations
    def __neg__(self):
        return Vec2d(operator.neg(self.x), operator.neg(self.y))

    def __pos__(self):
        return Vec2d(operator.pos(self.x), operator.pos(self.y))

    def __abs__(self):
        return Vec2d(abs(self.x), abs(self.y))

    def __invert__(self):
        return Vec2d(-self.x, -self.y)

    # vectory functions
    def get_length_sqrd(self):
        return self.x**2 + self.y**2

    def get_length(self):
        return math.sqrt(self.x**2 + self.y**2)
    def __setlength(self, value):
        length = self.get_length()
        self.x *= value/length
        self.y *= value/length
    length = property(get_length, __setlength, None, "gets or sets the magnitude of the vector")

    def rotate(self, angle_degrees):
        radians = math.radians(angle_degrees)
        cos = math.cos(radians)
        sin = math.sin(radians)
        x = self.x*cos - self.y*sin
        y = self.x*sin + self.y*cos
        self.x = x
        self.y = y

    def rotated(self, angle_degrees):
        radians = math.radians(angle_degrees)
        cos = math.cos(radians)
        sin = math.sin(radians)
        x = self.x*cos - self.y*sin
        y = self.x*sin + self.y*cos
        return Vec2d(x, y)

    def get_angle(self):
        if (self.get_length_sqrd() == 0):
            return 0
        return math.degrees(math.atan2(self.y, self.x))
    def __setangle(self, angle_degrees):
        self.x = self.length
        self.y = 0
        self.rotate(angle_degrees)
    angle = property(get_angle, __setangle, None, "gets or sets the angle of a vector")

    def get_angle_between(self, other):
        cross = self.x*other[1] - self.y*other[0]
        dot = self.x*other[0] + self.y*other[1]
        return math.degrees(math.atan2(cross, dot))

    def normalized(self):
        length = self.length
        if length != 0:
            return self/length
        return Vec2d(self)

    def normalize_return_length(self):
        length = self.length
        if length != 0:
            self.x /= length
            self.y /= length
        return length

    def perpendicular(self):
        return Vec2d(-self.y, self.x)

    def perpendicular_normal(self):
        length = self.length
        if length != 0:
            return Vec2d(-self.y/length, self.x/length)
        return Vec2d(self)

    def dot(self, other):
        return float(self.x*other[0] + self.y*other[1])

    def get_distance(self, other):
        return math.sqrt((self.x - other[0])**2 + (self.y - other[1])**2)

    def get_dist_sqrd(self, other):
        return (self.x - other[0])**2 + (self.y - other[1])**2

    def projection(self, other):
        other_length_sqrd = other[0]*other[0] + other[1]*other[1]
        projected_length_times_other_length = self.dot(other)
        return other*(projected_length_times_other_length/other_length_sqrd)

    def cross(self, other):
        return self.x*other[1] - self.y*other[0]

    def interpolate_to(self, other, range):
        return Vec2d(self.x + (other[0] - self.x)*range, self.y + (other[1] - self.y)*range)

    def convert_to_basis(self, x_vector, y_vector):
        return Vec2d(self.dot(x_vector)/x_vector.get_length_sqrd(), self.dot(y_vector)/y_vector.get_length_sqrd())

    def __getstate__(self):
        return [self.x, self.y]

    def __setstate__(self, dict):
        self.x, self.y = dict


class Vec3d(object):
    """3d vector class, supports vector and scalar operators,
        and also provides a bunch of high level functions.
        reproduced from the vec2d class on the pygame wiki site.
        """
    __slots__ = ['x', 'y', 'z']
 
    def __init__(self, x_or_triple, y = None, z = None):
        if y == None:
            self.x = x_or_triple[0]
            self.y = x_or_triple[1]
            self.z = x_or_triple[2]
        else:
            self.x = x_or_triple
            self.y = y
            self.z = z
 
    def __len__(self):
        return 3
 
    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        elif key == 2:
            return self.z
        else:
            raise IndexError("Invalid subscript "+str(key)+" to Vec3d")
 
    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        elif key == 2:
            self.z = value
        else:
            raise IndexError("Invalid subscript "+str(key)+" to Vec3d")
 
    # String representaion (for debugging)
    def __repr__(self):
        return 'Vec3d(%s, %s, %s)' % (self.x, self.y, self.z)
    
    # Comparison
    def __eq__(self, other):
        if hasattr(other, "__getitem__") and len(other) == 3:
            return self.x == other[0] and self.y == other[1] and self.z == other[2]
        else:
            return False
    
    def __ne__(self, other):
        if hasattr(other, "__getitem__") and len(other) == 3:
            return self.x != other[0] or self.y != other[1] or self.z != other[2]
        else:
            return True
 
    def __nonzero__(self):
        return self.x or self.y or self.z
 
    # Generic operator handlers
    def _o2(self, other, f):
        "Any two-operator operation where the left operand is a Vec3d"
        if isinstance(other, Vec3d):
            return Vec3d(f(self.x, other.x),
                         f(self.y, other.y),
                         f(self.z, other.z))
        elif (hasattr(other, "__getitem__")):
            return Vec3d(f(self.x, other[0]),
                         f(self.y, other[1]),
                         f(self.z, other[2]))
        else:
            return Vec3d(f(self.x, other),
                         f(self.y, other),
                         f(self.z, other))
 
    def _r_o2(self, other, f):
        "Any two-operator operation where the right operand is a Vec3d"
        if (hasattr(other, "__getitem__")):
            return Vec3d(f(other[0], self.x),
                         f(other[1], self.y),
                         f(other[2], self.z))
        else:
            return Vec3d(f(other, self.x),
                         f(other, self.y),
                         f(other, self.z))
 
    def _io(self, other, f):
        "inplace operator"
        if (hasattr(other, "__getitem__")):
            self.x = f(self.x, other[0])
            self.y = f(self.y, other[1])
            self.z = f(self.z, other[2])
        else:
            self.x = f(self.x, other)
            self.y = f(self.y, other)
            self.z = f(self.z, other)
        return self
 
    # Addition
    def __add__(self, other):
        if isinstance(other, Vec3d):
            return Vec3d(self.x + other.x, self.y + other.y, self.z + other.z)
        elif hasattr(other, "__getitem__"):
            return Vec3d(self.x + other[0], self.y + other[1], self.z + other[2])
        else:
            return Vec3d(self.x + other, self.y + other, self.z + other)
    __radd__ = __add__
    
    def __iadd__(self, other):
        if isinstance(other, Vec3d):
            self.x += other.x
            self.y += other.y
            self.z += other.z
        elif hasattr(other, "__getitem__"):
            self.x += other[0]
            self.y += other[1]
            self.z += other[2]
        else:
            self.x += other
            self.y += other
            self.z += other
        return self
 
    # Subtraction
    def __sub__(self, other):
        if isinstance(other, Vec3d):
            return Vec3d(self.x - other.x, self.y - other.y, self.z - other.z)
        elif (hasattr(other, "__getitem__")):
            return Vec3d(self.x - other[0], self.y - other[1], self.z - other[2])
        else:
            return Vec3d(self.x - other, self.y - other, self.z - other)
    def __rsub__(self, other):
        if isinstance(other, Vec3d):
            return Vec3d(other.x - self.x, other.y - self.y, other.z - self.z)
        if (hasattr(other, "__getitem__")):
            return Vec3d(other[0] - self.x, other[1] - self.y, other[2] - self.z)
        else:
            return Vec3d(other - self.x, other - self.y, other - self.z)
    def __isub__(self, other):
        if isinstance(other, Vec3d):
            self.x -= other.x
            self.y -= other.y
            self.z -= other.z
        elif (hasattr(other, "__getitem__")):
            self.x -= other[0]
            self.y -= other[1]
            self.z -= other[2]
        else:
            self.x -= other
            self.y -= other
            self.z -= other
        return self
 
    # Multiplication
    def __mul__(self, other):
        if isinstance(other, Vec3d):
            return Vec3d(self.x*other.x, self.y*other.y, self.z*other.z)
        if (hasattr(other, "__getitem__")):
            return Vec3d(self.x*other[0], self.y*other[1], self.z*other[2])
        else:
            return Vec3d(self.x*other, self.y*other, self.z*other)
    __rmul__ = __mul__
    
    def __imul__(self, other):
        if isinstance(other, Vec3d):
            self.x *= other.x
            self.y *= other.y
            self.z *= other.z
        elif (hasattr(other, "__getitem__")):
            self.x *= other[0]
            self.y *= other[1]
            self.z *= other[2]
        else:
            self.x *= other
            self.y *= other
            self.z *= other
        return self
 
    # Division
    def __div__(self, other):
        return self._o2(other, operator.div)
    def __rdiv__(self, other):
        return self._r_o2(other, operator.div)
    def __idiv__(self, other):
        return self._io(other, operator.div)
 
    def __floordiv__(self, other):
        return self._o2(other, operator.floordiv)
    def __rfloordiv__(self, other):
        return self._r_o2(other, operator.floordiv)
    def __ifloordiv__(self, other):
        return self._io(other, operator.floordiv)
 
    def __truediv__(self, other):
        return self._o2(other, operator.truediv)
    def __rtruediv__(self, other):
        return self._r_o2(other, operator.truediv)
    def __itruediv__(self, other):
        return self._io(other, operator.floordiv)
 
    # Modulo
    def __mod__(self, other):
        return self._o2(other, operator.mod)
    def __rmod__(self, other):
        return self._r_o2(other, operator.mod)
 
    def __divmod__(self, other):
        return self._o2(other, operator.divmod)
    def __rdivmod__(self, other):
        return self._r_o2(other, operator.divmod)
 
    # Exponentation
    def __pow__(self, other):
        return self._o2(other, operator.pow)
    def __rpow__(self, other):
        return self._r_o2(other, operator.pow)
 
    # Bitwise operators
    def __lshift__(self, other):
        return self._o2(other, operator.lshift)
    def __rlshift__(self, other):
        return self._r_o2(other, operator.lshift)
 
    def __rshift__(self, other):
        return self._o2(other, operator.rshift)
    def __rrshift__(self, other):
        return self._r_o2(other, operator.rshift)
 
    def __and__(self, other):
        return self._o2(other, operator.and_)
    __rand__ = __and__
 
    def __or__(self, other):
        return self._o2(other, operator.or_)
    __ror__ = __or__
 
    def __xor__(self, other):
        return self._o2(other, operator.xor)
    __rxor__ = __xor__
 
    # Unary operations
    def __neg__(self):
        return Vec3d(operator.neg(self.x), operator.neg(self.y), operator.neg(self.z))
 
    def __pos__(self):
        return Vec3d(operator.pos(self.x), operator.pos(self.y), operator.pos(self.z))
 
    def __abs__(self):
        return Vec3d(abs(self.x), abs(self.y), abs(self.z))
 
    def __invert__(self):
        return Vec3d(-self.x, -self.y, -self.z)
 
    # vectory functions
    def get_length_sqrd(self): 
        return self.x**2 + self.y**2 + self.z**2
 
    def get_length(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)      
    def __setlength(self, value):
        length = self.get_length()
        self.x *= value/length
        self.y *= value/length
        self.z *= value/length
    length = property(get_length, __setlength, None, "gets or sets the magnitude of the vector")
        
    def rotate_around_z(self, angle_degrees):
        radians = math.radians(angle_degrees)
        cos = math.cos(radians)
        sin = math.sin(radians)
        x = self.x*cos - self.y*sin
        y = self.x*sin + self.y*cos
        self.x = x
        self.y = y
 
    def rotate_around_x(self, angle_degrees):
        radians = math.radians(angle_degrees)
        cos = math.cos(radians)
        sin = math.sin(radians)
        y = self.y*cos - self.z*sin
        z = self.y*sin + self.z*cos
        self.y = y
        self.z = z
 
    def rotate_around_y(self, angle_degrees):
        radians = math.radians(angle_degrees)
        cos = math.cos(radians)
        sin = math.sin(radians)
        z = self.z*cos - self.x*sin
        x = self.z*sin + self.x*cos
        self.z = z
        self.x = x
 
    def rotated_around_z(self, angle_degrees):
        radians = math.radians(angle_degrees)
        cos = math.cos(radians)
        sin = math.sin(radians)
        x = self.x*cos - self.y*sin
        y = self.x*sin + self.y*cos
        return Vec3d(x, y, self.z)
    
    def rotated_around_x(self, angle_degrees):
        radians = math.radians(angle_degrees)
        cos = math.cos(radians)
        sin = math.sin(radians)
        y = self.y*cos - self.z*sin
        z = self.y*sin + self.z*cos
        return Vec3d(self.x, y, z)
    
    def rotated_around_y(self, angle_degrees):
        radians = math.radians(angle_degrees)
        cos = math.cos(radians)
        sin = math.sin(radians)
        z = self.z*cos - self.x*sin
        x = self.z*sin + self.x*cos
        return Vec3d(x, self.y, z)
    
    def get_angle_around_z(self):
        if (self.get_length_sqrd() == 0):
            return 0
        return math.degrees(math.atan2(self.y, self.x))
    def __setangle_around_z(self, angle_degrees):
        self.x = math.sqrt(self.x**2 + self.y**2)
        self.y = 0
        self.rotate_around_z(angle_degrees)
    angle_around_z = property(get_angle_around_z, __setangle_around_z, None, "gets or sets the angle of a vector in the XY plane")
 
    def get_angle_around_x(self):
        if (self.get_length_sqrd() == 0):
            return 0
        return math.degrees(math.atan2(self.z, self.y))
    def __setangle_around_x(self, angle_degrees):
        self.y = math.sqrt(self.y**2 + self.z**2)
        self.z = 0
        self.rotate_around_x(angle_degrees)
    angle_around_x = property(get_angle_around_x, __setangle_around_x, None, "gets or sets the angle of a vector in the YZ plane")
 
    def get_angle_around_y(self):
        if (self.get_length_sqrd() == 0):
            return 0
        return math.degrees(math.atan2(self.x, self.z))
    def __setangle_around_y(self, angle_degrees):
        self.z = math.sqrt(self.z**2 + self.x**2)
        self.x = 0
        self.rotate_around_y(angle_degrees)
    angle_around_y = property(get_angle_around_y, __setangle_around_y, None, "gets or sets the angle of a vector in the ZX plane")
 
    def get_angle_between(self, other):
        v1 = self.normalized()
        v2 = Vec3d(other)
        v2.normalize_return_length()
        return math.degrees(math.acos(v1.dot(v2)))
            
    def normalized(self):
        length = self.length
        if length != 0:
            return self/length
        return Vec3d(self)
 
    def normalize_return_length(self):
        length = self.length
        if length != 0:
            self.x /= length
            self.y /= length
            self.z /= length
        return length
 
    def dot(self, other):
        return float(self.x*other[0] + self.y*other[1] + self.z*other[2])
        
    def get_distance(self, other):
        return math.sqrt((self.x - other[0])**2 + (self.y - other[1])**2 + (self.z - other[2])**2)
        
    def get_dist_sqrd(self, other):
        return (self.x - other[0])**2 + (self.y - other[1])**2 + (self.z - other[2])**2
        
    def projection(self, other):
        other_length_sqrd = other[0]*other[0] + other[1]*other[1] + other[2]*other[2]
        projected_length_times_other_length = self.dot(other)
        return other*(projected_length_times_other_length/other_length_sqrd)
    
    def cross(self, other):
        return Vec3d(self.y*other[2] - self.z*other[1], self.z*other[0] - self.x*other[2], self.x*other[1] - self.y*other[0])
    
    def interpolate_to(self, other, range):
        return Vec3d(self.x + (other[0] - self.x)*range, self.y + (other[1] - self.y)*range, self.z + (other[2] - self.z)*range)
    
    def convert_to_basis(self, x_vector, y_vector, z_vector):
        return Vec3d(self.dot(x_vector)/x_vector.get_length_sqrd(),
            self.dot(y_vector)/y_vector.get_length_sqrd(),
            self.dot(z_vector)/z_vector.get_length_sqrd())
 
    def __getstate__(self):
        return [self.x, self.y, self.z]
        
    def __setstate__(self, dict):
        self.x, self.y, self.z = dict

