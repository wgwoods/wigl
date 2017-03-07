# wigl.kinect: get data from a Kinect device
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

import freenect
from freenect import *

class KinectError(IOError):
    pass

class Kinect(object):
    def __init__(self,
                 devno=0,
                 resolution=RESOLUTION_MEDIUM,
                 depth_mode=DEPTH_11BIT,
                 video_mode=VIDEO_RGB):
        self._ctx = freenect.init()
        if not self._ctx:
            raise KinectError("Cannot connect to device.")
        self.devno = devno
        self._dev = freenect.open_device(self._ctx, self.devno)
        if not self._dev:
            freenect.shutdown(self._ctx)
            raise KinectError("Cannot open device.")

        self._depth_callback = None
        self._video_callback = None

        self._resolution = resolution
        self.depth_mode = depth_mode
        self.video_mode = video_mode

    @property
    def depth_mode(self):
        return self._depth_mode

    @depth_mode.setter
    def depth_mode(self, mode):
        self._depth_mode = mode
        freenect.set_depth_mode(self._dev, self._resolution, mode)

    def start_depth(self, callback):
        freenect.start_depth(self._dev)
        self._depth_callback = callback
        return freenect.set_depth_callback(self._dev, callback)

    def stop_depth(self):
        freenect.stop_depth(self._dev)
        self._depth_callback = None

    def process_events(self):
        rv = freenect.process_events(self._ctx)
        if rv:
            raise KinectError("Error processing events", rv)

    def set_led(self, leds):
        return freenect.set_led(self._dev, leds)

    def shutdown(self):
        if self._dev:
            freenect.close_device(self._dev)
        if self._ctx:
            freenect.shutdown(self._ctx)
