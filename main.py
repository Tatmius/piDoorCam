from flask import Flask, render_template, Response, request
from camera import VideoCamera
from waitress import serve

pi_camera = VideoCamera(flipVert=True, flipHor=True)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', 
        framerate=pi_camera.camera.framerate,
        iso=pi_camera.camera.iso,
        shutter_speed=pi_camera.camera.shutter_speed)

def gen(camera):
    #get camera frame
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(pi_camera), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/set_daytime_mode')
def setDaytimeMode():
    pi_camera.setDaytimeMode()
    return render_template('index.html', 
        framerate=pi_camera.camera.framerate,
        iso=pi_camera.camera.iso,
        shutter_speed=pi_camera.camera.shutter_speed)

@app.route('/set_night_mode')
def setNightMode():
    pi_camera.setNightMode()
    return render_template('index.html', 
        framerate=pi_camera.camera.framerate,
        iso=pi_camera.camera.iso,
        shutter_speed=pi_camera.camera.shutter_speed)

if __name__ == '__main__':

    serve(app, host='0.0.0.0', port=5000)
    


