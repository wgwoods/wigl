# wigl.math: math modules for wigl.
#
# Copyright (C) 2014 Will Woods <will@wizard.zone>
#
# wigl is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# wigl is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with wigl.  If not, see <http://www.gnu.org/licenses/>.
#

import numpy as np

__all__ = [
    'norm', 'quat',
    'identity', 'translate', 'rotate', 'scale',
    'lookat', 'perspective', 'ortho',
]

def norm(v):
    '''Normalize a vector.'''
    mag = np.sqrt(v.dot(v))
    return v/mag if mag else v

def quat(angle, x, y, z):
    '''Return a normalized quaternion for the given rotation axis and angle'''
    a = np.radians(angle)/2
    c = np.cos(a)
    if c == 1.0: # no rotation - return identity
        return np.array([0,0,0,1], dtype=np.float32)
    else:
        s = np.sin(a)
        return norm(np.array([x*s, y*s, z*s, c], dtype=np.float32))

# XXX NOTE ONE: I'm using COLUMN-MAJOR matrices here, but numpy stores them
# as ROW-MAJOR by default (which transposes them) - so we need to transpose
# them again before we give them to OpenGL!

# XXX NOTE TWO: I'm assuming a left-handed coordinate system here (i.e. X is
# right, Y is up, Z is forward), but keep in mind that old OpenGL used to use
# a right-handed system for eye-space, so these functions vary slightly from
# their old GLU equivalents and/or random junk you'll find online..

def identity():
    return np.identity(4, dtype='float32')

def translate(x, y, z):
    '''Return a matrix representing a translation by (x,y,z).'''
    return np.matrix([
        [1, 0, 0, x],
        [0, 1, 0, y],
        [0, 0, 1, z],
        [0, 0, 0, 1],
    ], dtype=np.float32)

def rotateq(quat):
    # This is the quaternion version, wheeeee~~~~
    x, y, z, w = quat
    xx, yy, zz = x*x, y*y, z*z
    xy, xz, yz = x*y, x*z, y*z
    wx, wy, wz = w*x, w*y, w*z
    return np.matrix([
        [1-2*(yy+zz),   2*(xy-wz),   2*(xz+wy), 0],
        [  2*(xy+wz), 1-2*(xx+zz),   2*(yz-wx), 0],
        [  2*(xz-wy),   2*(yz+wx), 1-2*(xx+yy), 0],
        [          0,           0,           0, 1],
    ], dtype=np.float32)

def rotate(angle, x, y, z):
    '''Return a matrix representing rotation about the vector (x,y,z)'''
    # This is the glRotatef version
    a = np.radians(angle)
    c = np.cos(a)
    s = np.sin(a)
    x, y, z = norm(np.array([x,y,z]))
    xx, yy, zz = x*x, y*y, z*z
    xy, xz, yz = x*y, x*z, y*z
    xs, ys, zs = x*s, y*s, z*s
    oc = 1 - c
    return np.matrix([
        [xx*oc+c,  xy*oc-zs, xz*oc+ys, 0],
        [xy*oc+zs, yy*oc+c,  yz*oc-xs, 0],
        [xz*oc-ys, yz*oc+xs, zz*oc+c,  0],
        [       0,        0,       0,  1],
    ], dtype=np.float32)

def scale(x, y, z):
    '''Return a matrix for scaling along the x, y, and z axes.'''
    return np.matrix([
        [x, 0, 0, 0],
        [0, y, 0, 0],
        [0, 0, z, 0],
        [0, 0, 0, 1],
    ], dtype=np.float32)

def lookat(eye=(0,0,-1), center=(0,0,0), up=(0,1,0)):
    '''Return a view + transform matrix, similar to the one constructed by
       the deprecated gluLookAt() function.'''
    z = -norm(np.array(center)-np.array(eye))
    x = norm(np.cross(z, up))
    y = np.cross(x, z)
    # rotate world to camera orientation
    r = np.matrix([
        [x[0], x[1], x[2], 0],
        [y[0], y[1], y[2], 0],
        [z[0], z[1], z[2], 0],
        [   0,    0,    0, 1],
    ], dtype=np.float32)
    # translate inverse of eye position
    t = -np.array(eye)
    return r * translate(t[0], t[1], t[2])


def perspective(fovy=60, aspect=1.0, near=0.1, far=100):
    '''Return a perspective matrix, similar to the one constructed by the
       deprecated gluPerspective() function.'''
    f = 1/np.tan((np.pi/180)*(float(fovy)/2))
    a = 1/aspect
    z1 = float(far+near) / (near-far)
    z2 = float(2*far*near) / (near-far)
    return np.matrix([
        [f*a, 0,  0 , 0],
        [  0, f,  0,  0],
        [  0, 0, z1, z2],
        [  0, 0, -1,  0],
    ], dtype=np.float32)


def ortho(left=-1, right=1, bottom=-1, top=1, near=-1, far=1):
    '''Return an orthographic matrix, similar to the one constructed by the
       deprecated glOrtho() function.'''
    (l,r,b,t,n,f) = (left, right, bottom, top, near, far)
    return np.matrix([
        [2/(r-l), 0,       0,        -(r+l)/(r-l)],
        [0,       2/(t-b), 0,        -(t+b)/(t-b)],
        [0,       0,       2/(f-n),  -(f+n)/(f-n)],
        [0,       0,       0,                   1],
    ], dtype=np.float32)
