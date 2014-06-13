# __init__.py for wigl.
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
"""
WIGL: >WI<ll's >GL< library.

I wrote this to give myself a simple, python-y way to learn about (and
experiment with) modern (ish) OpenGL - i.e. OpenGL 3.3 or later.
(It'd be OpenGL 4.x but Mesa doesn't support that... yet.)
"""

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.arrays.vbo import VBO, VBOHandler

from .math import *

__all__ = [
    'WIGL', 'VBO',
    'DO_REDRAW', 'SKIP_REST', 'RESTART_INDEX',
    'ShaderProgram', 'VertexShader', 'FragmentShader',
]

# constants for returning from keyboard callback etc.
DO_REDRAW = 1
SKIP_REST = 2

# HA HA WHEE I LIKE THIS RESTART INDEX
RESTART_INDEX = 0xDEADBEEF

def enumstr(glenum):
    '''Given a GLenum (e.g. GL_SHADING_LANGUAGE_VERSION),
       return a human-readable string (e.g. 'Shading language version')'''
    if glenum.name.startswith("GL_"):
        return glenum.name[3:].lower().replace('_',' ').capitalize()

def glinfo(i):
    '''Convenience function - given a GLenum i, return a string of the form:
       "{human_readable(i)}: {glGetString(i)}"'''
    return "%s: %s" % (enumstr(i), glGetString(i))

class WIGL(object):
    def __init__(self,
                 name="WIGL",
                 size=(640,480),
                 mode=GLUT_DOUBLE|GLUT_RGB|GLUT_DEPTH,
                 clearcolor=(1,1,1,1),
                 ):
        self.mode = mode
        self.size = size

        glutInit() # XXX: sys.argv?
        glutInitContextVersion(3,3)
        glutInitContextFlags(GLUT_FORWARD_COMPATIBLE)
        glutInitContextProfile(GLUT_CORE_PROFILE)
        glutInitDisplayMode(mode)
        glutInitWindowSize(*size)
        self.window = glutCreateWindow(name)

        # twiddle GL stuff now that we have a window
        print glinfo(GL_VENDOR)
        print glinfo(GL_VERSION)
        print glinfo(GL_SHADING_LANGUAGE_VERSION)
        print glinfo(GL_RENDERER)

        glClearColor(*clearcolor)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        glEnable(GL_PRIMITIVE_RESTART)
        glPrimitiveRestartIndex(RESTART_INDEX)

        # set default view/perspective/model matrices
        self.lookat()
        self.ortho()
        self.resetmodel()

        # set up the default callbacks
        glutDisplayFunc(self._display_cb)
        glutReshapeFunc(self._resize_cb)
        glutKeyboardFunc(self._keyboard_cb)

        # Disable the idle callback unless our subclass defined one
        if hasattr(self, 'idle') and callable(self.idle):
            glutIdleFunc(self.idle)
        else:
            glutIdleFunc(None)

        # create a VBO and do the user-defined interesting setup bits
        self.vao = VAO()
        with self.vao:
            self.setup()

        # now we should have shaders, so we can apply perspective
        self.apply_matrices()

    @property
    def aspect(self):
        return float(self.size[0])/self.size[1]

    def lookat(self, eye=(0,0,-1), center=(0,0,0), up=(0,1,0)):
        self.view = lookat(eye, center, up)

    def perspective(self, fovy=45, near=0.1, far=10.0):
        self.projection = perspective(fovy, self.aspect, near, far)

    def ortho(self, left=-1, right=1, bottom=-1, top=1, near=-1, far=1):
        self.projection = ortho(left, right, bottom, top, near, far)

    def resetmodel(self):
        '''Reset the model matrix to the identity.'''
        self.model = identity()

    def translate(self, x, y, z):
        '''Translate the model by (x,y,z)'''
        self.model = translate(x,y,z) * self.model

    def rotate(self, angle, x, y, z):
        '''Rotate the model around the given vector (x,y,z)'''
        self.model = rotate(angle, x,y,z) * self.model

    def scale(self, x, y, z):
        '''Scale the model along the x, y, and z axes by the given factors'''
        self.model = scale(x,y,z) * self.model

    def apply_matrices(self):
        proj = self.shaders.get_uniform('projection')
        view = self.shaders.get_uniform('view')
        model = self.shaders.get_uniform('model')
        with self.shaders:
            # True -> "matrix is row-major, transpose before use"
            glUniformMatrix4fv(proj, 1, True, self.projection)
            glUniformMatrix4fv(view, 1, True, self.view)
            glUniformMatrix4fv(model, 1, True, self.model)

    def timer(self, msecs, func, value=None, repeat=False):
        if repeat:
            def wrapped_func(value):
                func(value)
                glutTimerFunc(msecs, wrapped_func, value)
            glutTimerFunc(msecs, wrapped_func, value)
        else:
            glutTimerFunc(msecs, func, value)

    def redraw(self):
        glutPostRedisplay()

    def quit(self):
        glutLeaveMainLoop()

    def _display_cb(self):
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        with self.shaders, self.vao:
            r = self.display()
        if self.mode & GLUT_DOUBLE:
            glutSwapBuffers()

    def _keyboard_cb(self, key, x, y):
        r = self.keyboard(key, x, y)
        if r == DO_REDRAW:
            self.redraw()
        if r == SKIP_REST:
            return
        if ord(key) == 27:
            self.quit()

    def _resize_cb(self, width, height):
        oldw, oldh = self.size
        # XXX does this DTRT for ortho?
        self.projection[0][0] *= (float(oldw)/oldh)/(float(width)/height)
        self.size = (width, height)
        self.apply_matrices()
        glViewport(0, 0, self.size[0], self.size[1])

    # Here are the functions we should actually define in our stuff.

    def setup(self):
        pass

    def display(self):
        pass

    def keyboard(self, key, x, y):
        pass

    # aaaand mainloop!

    def mainloop(self):
        glutMainLoop()

class VAO(object):
    """A Vertex Array Object.
       Think of this as an object that encapsulates buffer state, so rather
       than having to individually bind each of your VBOs etc. in your draw
       loop, you set them up and bind them to the *VAO*.
       Then you just bind the VAO you want to use for each draw loop and
       GL does the rest.
    """
    def __init__(self):
        self._id = None

    @property
    def id(self):
        if self._id is None:
            self._id = glGenVertexArrays(1)
        return self._id

    def bind(self):
        glBindVertexArray(self.id)

    def unbind(self, *args):
        glBindVertexArray(0)

    __enter__ = bind
    __exit__  = unbind

class ShaderProgram(object):
    def __init__(self, *shaders):
        self.id = glCreateProgram()
        self.vbolist = []
        for shader in shaders:
            shader.compile()
            glAttachShader(self.id, shader.id)
        glLinkProgram(self.id)

        # clean up shaders
        if self.prog_ok():
            for shader in shaders:
                glDeleteShader(shader.id)

    def prog_ok(self):
        glValidateProgram(self.id)
        if not glGetProgramiv(self.id, GL_VALIDATE_STATUS):
            raise RuntimeError("Validation failed: %s" % \
                                glGetProgramInfoLog(self.id))
        if not glGetProgramiv(self.id, GL_LINK_STATUS):
            raise RuntimeError("Link failed: %s" % \
                                glGetProgramInfoLog(self.id))

    def bind_attr(self, name, thisvbo, size=None, gltype=None, normalized=False,
                  stride=0, offset=None):
        attr_id = glGetAttribLocation(self.id, name)
        if gltype is None:
            gltype = VBOHandler().arrayToGLType(thisvbo)
        if size is None:
            size = VBOHandler().unitSize(thisvbo)
        thisvbo.bind()
        glEnableVertexAttribArray(attr_id)
        glVertexAttribPointer(attr_id, size, gltype, normalized, stride, offset)
        self.vbolist.append(thisvbo)

    def get_uniform(self, name):
        return glGetUniformLocation(self.id, name)

    def use(self):
        glUseProgram(self.id)

    def stop(self, *args):
        glUseProgram(0)

    __enter__ = use
    __exit__  = stop

class Shader(object):
    def __init__(self, source, shadertype):
        self.id = None
        self.source = source
        self.type = shadertype

    def compile(self):
        self.id = glCreateShader(self.type)
        glShaderSource(self.id, self.source)
        glCompileShader(self.id)
        if not glGetShaderiv(self.id, GL_COMPILE_STATUS):
            raise RuntimeError(
                "Shader compile failure: %s" % glGetShaderInfoLog(self.id),
                self.source,
                self.type,
            )

class VertexShader(Shader):
    def __init__(self, source):
        super(VertexShader, self).__init__(source, GL_VERTEX_SHADER)

class FragmentShader(Shader):
    def __init__(self, source):
        super(FragmentShader, self).__init__(source, GL_FRAGMENT_SHADER)

class Texture(object):
    def __init__(self, data, texturetype, glformat, pixelformat, pixeltype):
        self.id = None
        self.unit = 0
        self.data = data
        self.texturetype = texturetype
        self.glformat = glformat
        self.pixelformat = pixelformat
        self.pixeltype = pixeltype

    def bind(self, unit=0):
        self.unit = unit
        glActiveTexture(GL_TEXTURE0 + self.unit)
        if self.id is None:
            self.id = glGenTextures(1)
        glBindTexture(self.texturetype, self.id)

    def load(self, unit=0, mode=GL_LINEAR):
        self.bind(unit)
        self.loadimg()
        glTexParameteri(self.texturetype, GL_TEXTURE_MIN_FILTER, mode)
        glTexParameteri(self.texturetype, GL_TEXTURE_MAG_FILTER, mode)

    def replace(self, data):
        glBindTexture(self.texturetype, self.id)
        self.replaceimg(data)

    def delete(self):
        glDeleteTextures(1, self.id)

class Texture2D(Texture):
    def loadimg(self):
        glTexImage2D(self.texturetype,   # target
                     0,                  # level
                     self.glformat,      # internalFormat
                     self.data.shape[1], # width
                     self.data.shape[0], # height
                     0,                  # border. "This value must be 0."
                     self.pixelformat,   # format
                     self.pixeltype,     # type
                     self.data[::-1,...])# image data (flipped vertically)

    def replaceimg(self, data, xoff=0, yoff=0):
        glTexSubImage2D(self.texturetype,
                        0,
                        xoff,
                        yoff,
                        data.shape[1],
                        data.shape[0],
                        self.pixelformat,
                        self.pixeltype,
                        data[::-1,...])
