#!/usr/bin/env python
# client.py

# imports
try:
    import imagezmq
except ImportError:
    print("The python package imagezmq is required.")
    exit(1)
try:
    from imutils.video import VideoStream
except ImportError:
    print("The python package imutils is required.")
    exit(1)
import socket
import argparse

# construct argparser
ap = argparse.ArgumentParser()
ap.add_argument("-s", "--server",
                help="IP-Address of the server to connect to.")
args = vars(ap.parse_args())

server = "10.0.60.1"
if args["server"]:
    server = args["server"]
    

# Get hostname as name for stream
hname = socket.gethostname()

# Init sender object
sender = imagezmq.ImageSender(connect_to="tcp://%s:5555" %(server))

# Init video stream
vs = VideoStream(0).start()

try:
    while True:
        # read vs and send it to server
        frame = vs.read()
        sender.send_image(hname, frame)
except (KeyboardInterrupt, SystemExit):
    pass 
except Exception as e:
    print(e)
finally:
    vs.stop()
    sender.close()
    exit(1)