#!/usr/bin/env python
# server.py

# imports
try:
    import face_recognition
except ImportError:
    print("The python package face_recognition is required.")
    exit(1)
try:
    import imutils
except ImportError:
    print("The python package imutils is required.")
    exit(1)
try:
    import imagezmq
except ImportError:
    print("The python package imagezmq is required.")
    exit(1)
try:
    import pickle
except ImportError:
    print("The python package pickle is required.")
    exit(1)
try:
    import cv2
except ImportError:
    print("The python package opencv-python is required.")
    exit(1)
try:
    import netifaces as ni
except ImportError:
    print("The python package netifaces is required.")
    exit(1)
try:
    from esp_proxy import EspProxy
except ImportError:
    print("The file esp_proxy.py is required.")
    exit(1)
try:
    from mqtt import Client as mqttClient
except ImportError:
    print("The file mqtt.py is required.")
    exit(1)

import time
from datetime import datetime
import os
import argparse


# a little beauty for logging
class log:
    INIT_OK = '[\033[1m\033[92mOK\033[0m] '
    INIT_FAIL = '[\033[91m\033[1mX\033[0m] '
    INFO = '[*] '
 
 
# construct argparser
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--interface",
                help="Define WiFi-Interface the AP is running at")
ap.add_argument("-e", "--noesp", const=True, default=False, nargs="?",
                help="Deactivates EspProxy for supporting ESP32-Cams")
ap.add_argument("-v", "--visual", const=True, default=False, nargs="?",
                help="Enabled visual output")
ap.add_argument("-c", "--columns", type=int, default=4, nargs="?", 
                help="Set max number of frames in a row (visual-mode only)")
ap.add_argument("-t", "--test", const=True, default=False, nargs="?",
                help="Testrun of the server without any function")
args = vars(ap.parse_args())

# Print run-mode
if args["visual"]:
    print(log.INIT_OK + "Server started in visual-mode")
elif args["test"]:
    print(log.INIT_OK + "Server started for test-run")

server_ip = "127.0.0.1"
if not args["test"]:
    if not args["interface"]:
        print(log.INIT_FAIL + "Please define the interface the AP is running at!")
        exit(1)
    # get ip address of access point
    server_ip = ni.ifaddresses(args["interface"])[ni.AF_INET][0]['addr']
    
    # load encoded faces
    try:
        data = pickle.loads(open('data/face_enc', "rb").read())
        print(log.INIT_OK + "Succesfully loaded face-encodings")
    except Exception as e:
        print(log.INIT_FAIL + "Face-encodings not found")
        exit(1)
     
 
# load haarcascade file
faced = cv2.CascadeClassifier("data/haarcascade_frontalface_alt2.xml")

# create dict-objects for storing frames and their last streaming time
frameDict = {}
lastActive = {}

lastActiveCheck = datetime.now()

# Initialize ImageZMQ Hub 
Hub = imagezmq.ImageHub()

# check for success
if(Hub):
    print(log.INIT_OK + "Started ImageZMQ-Hub")
else:
    print(log.INIT_FAIL + "Failed starting ImageZMQ-Hub" )
    exit(1)

if not args["noesp"]:
# Initialize EspProxy    
    esp = EspProxy(server_ip)
    try:
        esp.start()
        print(log.INIT_OK + "Started EspProxy")
    except Exception as e:
        print(log.INIT_FAIL + e)
    
# Initialize Mqtt
broker = server_ip
port = 1883
mqtt = mqttClient(broker, port, "Server")

mqttBlocktime = 5 # Block sending new msgs for x seconds
mqttBlocklist = {}


try:
    mqtt.start()
    print(log.INIT_OK + "MQTT-Connection established")
except Exception as e:
    print(log.INIT_FAIL + e)


if args["test"]:
    print(log.INIT_OK + "Testrun completed. Exiting..")
    exit(1)
else:
    print(log.INIT_OK + "Server started")
print(log.INFO + "Waiting for clients")

try:
    # main-loop for processing frames
    while True:
        (source, frame) = Hub.recv_image()
        Hub.send_reply(b'OK')
        
        frame = imutils.resize(frame,width=500)
        
        if source not in lastActive.keys():
            print(log.INFO + "Receiving from %s" %(source))
        
        lastActive[source] = datetime.now()
        
        (h,w) =  frame.shape[:2]

        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY) # convert for face detection
        rgb = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB) # convert for face recognition
        
        # detect faces
        rects = faced.detectMultiScale(gray, scaleFactor=1.1,minNeighbors=5, minSize=(30,30))
        
        # reorder given coordinates
        boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]
        
        # prepare detected faces
        encodings = face_recognition.face_encodings(rgb, boxes)
        names = []
        
        # loop through encoded faces and find the best match
        for encoding in encodings:
            matches = face_recognition.compare_faces(data["encodings"], encoding)
            name = "Unknown"
            
            if True in matches:
                matchedIdxs = [i for (i,b) in enumerate(matches) if b]
                counts = {}
            
                for i in matchedIdxs:
                    name = data["names"][i]
                    counts[name] = counts.get(name,0) + 1
                    
                name = max(counts, key=counts.get)
                
            names.append(name)
            
        # publish mqtt msg
        for name in names:
            if name not in mqttBlocklist:
                if name == "Unknown":
                    mqtt.publish("Unknown", "1")
                    mqttBlocklist[name] = datetime.now()
                else:
                    mqtt.publish("Known", "1")
                    mqttBlocklist[name] = datetime.now()
        
        # only print visual boxes in visual mode
        if(args["visual"]):
            for ((top, right, bottom, left), name) in zip(boxes, names):
                # mark recognised face in videostream
                if name == "Unknown":
                    color = (0,0,255)
                else:
                    color = (0,255,0)
                cv2.rectangle(frame, (left, top), (right,bottom), color, 2) 
                cv2.putText(frame, name, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)


        frameDict[source] = frame
        
        mH = 1
        mW = args["columns"]
        numFrames = len(frameDict)
        if numFrames <= mW:
            mW = numFrames
        else:
            count = 0
            for i in numFrames:
                if count == mW:
                    mH += 1
                    count = 0
                else:
                    count += 1
        
        
        # only in visual mode
        if(args["visual"]):    
            cv2.putText(frame, source, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0),1, cv2.LINE_AA, False)
            
            # calculate matrix for montage
            mH = 1
            mW = args["columns"]
            numFrames = len(frameDict)
            if numFrames <= mW:
                mW = numFrames
            else:
                count = 0
                for i in numFrames:
                    if count == mW:
                        mH += 1
                        count = 0
                    else:
                        count += 1
            
            # show montage
            montages = imutils.convenience.build_montages(frameDict.values(), (w,h), (mH, mW))
            for (i, montage) in enumerate(montages):
                cv2.imshow("Camera Overview ({})".format(i), montage)
        
        
        if (datetime.now() - lastActiveCheck).seconds > 5:
            # manage frames
            for(source, ts) in list(lastActive.items()):
                if (datetime.now() - ts).seconds > 5:
                    print(log.INFO + "Lost connection to %s" %(source))
                    lastActive.pop(source)
                    frameDict.pop(source)
                    if not args["noesp"]:
                        esp.lost_connection(source)
            # manage Mqtt-Blocking
            for(topic, ts) in list(mqttBlocklist.items()):
                if (datetime.now() - ts).seconds > mqttBlocktime:
                    mqttBlocklist.pop(topic)
            lastActiveCheck = datetime.now()

        # exit-key for window
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
except (KeyboardInterrupt, SystemExit):
    pass 
except Exception as e:
    print(e)
finally:
    Hub.close()
    cv2.destroyAllWindows()