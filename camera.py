import cv2
import time
import numpy as np
import atexit

from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread


class VideoCamera(object):
    def __init__(self, resolution=(1296, 972), framerate=30, iso=200, flipVert = False, flipHor = False, **kwargs):
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.camera.iso = iso
        self.camera.shutter_speed = 0

        for (arg, value) in kwargs.items():
          setattr(self.camera, arg, value)

        # initialize the stream
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True)

        self.frame = None
        self.stopped = False

        self.vs = self.start()
        self.flipVert = flipVert
        self.flipHor = flipHor

        atexit.register(self.camera.close)

        time.sleep(2.0)
    
    def __del__(self):
        self.vs.stop()
        self.camera.close()
    
    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self
    
    def update(self):
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
          # grab the frame from the stream and clear the stream in
          # preparation for the next frame
          self.frame = f.array
          self.rawCapture.truncate(0)

          # if the thread indicator variable is set, stop the thread
          # and resource camera resources
          if self.stopped:
            self.stream.close()
            self.rawCapture.close()
            self.camera.close()
            return

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True

    def restart(self):
        self.stopped = False

    def flip_vert(self, frame):
        #flip video vertically
        if self.flipVert:
            return np.flip(frame, 0)
        return frame

    def flip_hor(self, frame):
        #flip video horizontally
        if self.flipHor:
            return np.flip(frame, 1)
        return frame
    
    def rotate(self, frame):
        return np.rot90(frame)
    
    def get_frame(self):
        frame = self.rotate(self.flip_hor(self.flip_vert(self.vs.read())))
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()
    
    def setNightMode(self):
        self.camera.iso = 800
        self.camera.exposure_mode = 'off'
        self.camera.shutter_speed = 6000000
        self.camera.framerate = 0.1
        time.sleep(7)

    def setDaytimeMode(self):
        self.camera.iso = 200
        self.camera.exposure_mode = 'off'
        self.camera.shutter_speed = 0
        self.camera.framerate = 30