# wigl.pbm: routines to read PBM-format texture files
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
from wigl import Texture2D
from OpenGL.GL import *

def readpbm(filename):
    with open(filename, "rb") as pbm:
        (magic, width, height, maxval) = pbm.readline().split()
        d = np.fromfile(pbm, dtype=np.uint8 if int(maxval) < 256 else np.uint16)

    if magic == "P5":
        d.shape = (int(height),int(width))   # grayscale
    elif magic == "P6":
        d.shape = (int(height),int(width),3) # RGB

    return d

class PBMTexture(Texture2D):
    def __init__(self, data, texturetype):
        super(PBMTexture, self).__init__(data, texturetype,
            GL_RGB if len(data.shape) == 3 else GL_R16,
            GL_RGB if len(data.shape) == 3 else GL_RED,
            GL_UNSIGNED_BYTE if data.dtype == np.uint8 else GL_UNSIGNED_SHORT
        )

def pbm_texture(filename, texturetype=GL_TEXTURE_2D):
    return PBMTexture(readpbm(filename), texturetype)

def kinect_texture(filename, texturetype=GL_TEXTURE_2D):
    data = readpbm(filename)
    return PBMTexture(data, texturetype)
