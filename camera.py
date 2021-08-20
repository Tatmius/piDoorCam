#Modified by smartbuilds.io
#Date: 27.09.20
#Desc: This scrtipt script..

import cv2
from imutils.video.pivideostream import PiVideoStream
import imutils
import time
import numpy as np

from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread

import atexit


class VideoCamera(object):
    def __init__(self, flipVert = False, flipHor = False):
        self.vs = PiVideoStream().start()
        self.flipVert = flipVert
        self.flipHor = flipHor
        time.sleep(2.0)

    def __del__(self):
        self.vs.stop()

    def flip_vert(self, frame):
        if self.flipVert:
            return np.flip(frame, 0)
        return frame

    def flip_hor(self, frame):
        if self.flipHor:
            return np.flip(frame, 1)
        return frame
		
    def rotate(self, frame):
		    return np.rot90(frame)

    def get_frame(self):
        frame = self.rotate(self.flip_hor(self.flip_vert(self.vs.read())))
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

    def stop(self):
        self.vs.stop()
        print("now camera is stopped")
    
    def restart(self):
        self.vs.restart()
        print("now camera is started")


#original code is imustils Pivideostream
class PiVideoStream:
	def __init__(self, resolution=(1280, 720), framerate=32, **kwargs):
		# initialize the camera
		self.camera = PiCamera()
		atexit.register(self.close_camera)

		# set camera parameters
		self.camera.resolution = resolution
		self.camera.framerate = framerate

		# set optional camera parameters (refer to PiCamera docs)
		for (arg, value) in kwargs.items():
			setattr(self.camera, arg, value)

		# initialize the stream
		self.rawCapture = PiRGBArray(self.camera, size=resolution)
		self.stream = self.camera.capture_continuous(self.rawCapture,
			format="bgr", use_video_port=True)

		# initialize the frame and the variable used to indicate
		# if the thread should be stopped
		self.frame = None
		self.stopped = False

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
		# return the frame most recently read
		return self.frame

	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True

        def restart(self):
                self.stopped = False
	
	def close_camera(self):
		self.camera.close()
