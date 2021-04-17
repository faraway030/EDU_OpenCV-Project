#!/usr/bin/env python
# esp_proxy.py

import imagezmq
import socket
from threading import Thread
from imutils.video import VideoStream

class EspCam(object):
    def __init__(self, server, cam_ip, cam_name):
        self.name = cam_name
        self.stream = VideoStream("http://%s/" %(cam_ip))
        self.stream.start()
        self.frame = self.stream.read()
        self.stopped = False
        self.sender = imagezmq.ImageSender(connect_to="tcp://%s:5555" %server)
        self.start()
    
    def start(self):
        while not self.stopped:
            self.frame = self.stream.read()
            if self.frame is None:
                self.stop()
            else:
                self.sender.send_image(self.name, self.frame)
        self.stream.stop()
        return
    
    def stop(self):
        self.stopped = True

class EspProxy(object):
    def __init__(self, server):
        self.HOST = server
        self.PORT = 44444
        self.s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.s.bind((self.HOST,self.PORT))
        self.clients = {}
        
    def start(self):
        Thread(target=self.wait_for_clients, args=(), daemon=True).start()
 
    def handle_client(self, client, name):
        self.clients[client] = Thread(target=EspCam, args=(self.HOST, client, name), daemon=True)
        self.clients[client].start()
    
    def lost_connection(self, client):
        self.clients.pop(client)
    
    def wait_for_clients(self):
        BUFFERSIZE = 1024
        while True:
            data, client = self.s.recvfrom(BUFFERSIZE)
            client = client[0]
            name = data.decode("utf-8")
            if "CAM" in name:
                self.handle_client(client,name)     
    
    def stop(self):
        self.s.close()
        
if __name__ == '__main__':
    esp = EspProxy("localhost")
    esp.start()