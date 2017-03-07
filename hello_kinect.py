#!/usr/bin/python
# 
# hello_kinect.py - simple test program to do 3D stuff with a Kinect!
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

from OpenGL.GL import *

from wigl import WIGL, VBO, DO_REDRAW, RESTART_INDEX
from wigl import ShaderProgram, VertexShader, FragmentShader, Texture2D

from wigl.mesh import simplemesh, triangle_mesh_indexes
from wigl.kinect import Kinect, KinectError

import numpy as np

class Heightmap(WIGL):
    def setup(self):
        self.rotation = False
        self.rotcounter = 0.0
        self.frames = 0
        self.texture = None

        # set up projection + view matrices
        self.center = [0,0,0]
        self.eye = [0,0,-1.5]
        self.perspective(fovy=60)
        self.lookat(center=self.center, eye=self.eye)

        # Define our shaders
        self.shaders = ShaderProgram(
            VertexShader("""
                #version 330
                in vec2 meshpos;
                in vec3 color;
                smooth out vec4 frag_color;
                uniform mat4 projection;
                uniform mat4 view;
                uniform mat4 model;
                uniform sampler2D heightmap;
                void main() {
                    // Find the height value that corresponds to this grid point
                    float aspect = 4.0/3.0; // FIXME: uniform
                    vec2 texpos = vec2((meshpos.x+aspect)/(2*aspect),
                                       (meshpos.y+1)/2);
                    vec4 hmpos = texture(heightmap, texpos);

                    // Construct the vertex accordingly
                    vec4 position = vec4(1.0);
                    position.xy = meshpos;
                    // Convert depth from raw data to (approximate) meters
                    hmpos.r = clamp(hmpos.r, 500.0/65536.0, 1000.0/65536.0);
                    position.z = 0.1236*tan(hmpos.r*23.05576+1.1863) - 0.5;
                    position.z = clamp(position.z, 0.0, 2.0);

                    gl_Position = projection * view * model * position;

                    // oh yeah, color
                    frag_color = vec4(color, 1.0);

                    // vary color by coordinates so I can be sure it works
                    frag_color.r += position.x;
                    frag_color.g += position.y;
                    frag_color.b += position.z;
                }
            """),
            FragmentShader("""
                #version 330
                smooth in vec4 frag_color;
                out vec4 out_color;
                void main() {
                    out_color = frag_color;
                }
            """)
        )
        # Create the VBO containing vertex data
        self.vertex_vbo = VBO(simplemesh(320,240,aspect=self.aspect))
        self.shaders.bind_attr('meshpos', self.vertex_vbo)

        # Create a VBO for index data for triangles
        self.tri_idx = VBO(triangle_mesh_indexes(self.vertex_vbo),
                                 target=GL_ELEMENT_ARRAY_BUFFER)

        # Color data!
        colors = ((1,0,0),(0,1,0),(0,0,1))
        self.color_vbo = VBO(np.array([
            colors[(i%4)/2] for i in xrange(self.vertex_vbo.data.size)
        ], dtype=np.float32))
        self.shaders.bind_attr('color', self.color_vbo)

        # update rotation every 10ms
        self.timer(10, self.rotate_model, repeat=True)

        # set up the kinect callback
        self.kinect = Kinect()
        self.kinect.start_depth(self.new_depth_frame)

    def idle(self):
        try:
            self.kinect.process_events()
        except KinectError as e:
            print e
            self.quit()

    def keyboard(self, key, x, y):
        if key == " ":
            self.rotation = not self.rotation
        elif key == "r":
            self.resetmodel()
        elif key == "a":
            self.eye[0] -= 0.1
        elif key == "d":
            self.eye[0] += 0.1
        elif key == "w":
            self.eye[2] += 0.1
        elif key == "s":
            self.eye[2] -= 0.1
        elif key == "e":
            self.eye[1] += 0.1
        elif key == "q":
            self.eye[1] -= 0.1

        if key in "wasdeqr":
            print "center: %s" % self.center
            print "eye: %s" % self.eye
            self.lookat(center=self.center, eye=self.eye)
            self.apply_matrices()

        return DO_REDRAW

    def new_depth_frame(self, dev, data, timestamp):
        if not self.texture:
            self.texture = Texture2D(data, GL_TEXTURE_2D,
                                     GL_R16, GL_RED, GL_UNSIGNED_SHORT)
            self.texture.load()
        else:
            self.texture.replace(data)
        heightmap = self.shaders.get_uniform("heightmap")
        with self.shaders:
            glUniform1i(heightmap, self.texture.unit)
        self.frames += 1
        self.redraw()

    def display(self):
        self.tri_idx.bind()
        glDrawElements(GL_TRIANGLE_STRIP, self.tri_idx.data.size,
                       GL_UNSIGNED_INT, None)

    def rotate_model(self, value):
        # rotate model around the y axis
        if self.rotation:
            self.rotcounter += 0.01
            self.resetmodel()
            self.rotate(self.rotcounter*45, 0,1,0)
            self.apply_matrices()
            self.redraw()
        self.idle()

if __name__ == '__main__':
    w = Heightmap()
    w.mainloop()
