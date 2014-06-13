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
