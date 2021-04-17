# EDU_OpenCV-Project

## Description
This is an educational project I made during Raspberry Pi class in my retraining. Since I'm using Raspberry Pi's for years now I wanted to do some more than just installing a webserver on it. Because my trainer asked me to include some micro-controllers in my project, I decided to build a client/server-application for face-recognition.<br>
<br>
Goal of this project was to send the videostream of the cameras to the Pi 4, which is processing the frames to recognize faces. If a face is detected, the Pi 4 should send a signal to the D1 mini, which shows if the face is known or not by lighting a green or red LED.


### Parts used:
- Raspberry Pi 4
- Raspberry Pi Zero W
- Raspberry Pi Camera
- ESP32-CAM Development Board
- D1 mini Development Board
- 3 LEDs and some jumper cables

### Software used:
- OpenCV
- dlib 
- ImageZMQ

### Demonstration
![Demo GIF Image](demo.gif)

## Documentation
You can find my complete documentation in german language [here](https://github.com/faraway030/EDU_OpenCV-Project/blob/master/doc/EDU_OpenCV-Project.pdf).

