#!/usr/bin/env python
# mqtt.py

import paho.mqtt.client as mqttClient
from time import sleep

class Client(object):
    def __init__(self,broker, port, clientId):
        self.broker = broker
        self.port = port
        self.client = mqttClient.Client(clientId)
        self.Connected = False
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.Connected = True                #Signal connection 
        else:
            pass
            
    def start(self):
        self.client.on_connect = self.on_connect
        self.client.connect(self.broker, port=self.port)
        self.client.loop_start()
        while self.Connected != True:
            sleep(0.1)
    
    def stop(self):
        self.client.disconnect()
        self.client.loop_stop()
        
    def publish(self, topic, value):
        self.client.publish("cmnd/OpenCV/%s" %(topic), value)