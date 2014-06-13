#!/usr/bin/python

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
