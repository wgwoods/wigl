# wigl.mesh: mesh modules for wigl.
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

from . import RESTART_INDEX

import numpy as np

__all__ = [
    'makemesh', 'simplemesh', 'triangle_mesh_indexes',
]

def makemesh(xvec, zvec):
    return np.dstack(np.meshgrid(xvec, zvec)).astype(np.float32)

def simplemesh(numx, numz, aspect=1):
    return makemesh(np.linspace(-aspect,aspect,numx),np.linspace(-1,1,numz))

def triangle_mesh_indexes(mesh):
    rows, cols, _ = mesh.shape
    out = list()
    for i in xrange(cols*(rows-1)):
        if i and (i % cols) == 0: out.append(RESTART_INDEX)
        out += [i, i+cols]
    return np.array(out, dtype=np.uint32)
