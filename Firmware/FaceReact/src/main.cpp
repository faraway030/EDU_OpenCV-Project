#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <PubSubClient.h>

// Define WiFi Credentials
const char* WIFI_SSID = "FPA-OpenCV";
const char* WIFI_PASS = "BoeckBoeck";

// Define MQTT Data
const char* MQTT_BROKER = "10.0.60.1";
String clientId = "FaceReact";
const char* cTopic_K = "cmnd/OpenCV/Known";
const char* sTopic_K = "stat/OpenCV/Known";
const char* cTopic_U = "cmnd/OpenCV/Unknown";
const char* sTopic_U = "stat/OpenCV/Unknown";

// Define LED Pins
int ledG = 14;
int ledR = 12;
int ledB = 13;

WiFiClient espClient;
PubSubClient client(espClient);

unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE	(50)
char msg[MSG_BUFFER_SIZE];
int value = 0;

// Resettimer
unsigned long TimerG = 0;
unsigned long TimerR = 0;
unsigned long resetTime = 10 * 1000; // Reset state after 10 seconds

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (unsigned int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }

  // Switch on the LED if an 1 was received as first character
  if ((char)payload[0] == '1') {
    if(!strcmp(topic,cTopic_K)) {
      Serial.println("Turn turn green led on");
      TimerG = millis();
      digitalWrite(ledG, HIGH);
    }
    else if(!strcmp(topic,cTopic_U)) {
      Serial.println("Turn turn red led on");
      TimerR = millis();
      digitalWrite(ledR, HIGH);
    }
  } 
}

void reconnect() {
  // Loop until connection is established
  while (!client.connected()) {
    Serial.println("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      // Subscribe to mqtt topic
      client.subscribe(cTopic_K);
      client.subscribe(cTopic_U);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void checkReset() {
  if ((millis() > TimerR + resetTime) &&
    (digitalRead(ledR) == HIGH))
  {
      digitalWrite(ledR,LOW);
      client.publish(sTopic_U, "0");
  }
  if ((millis() > TimerG + resetTime) &&
    (digitalRead(ledG) == HIGH))
  {
      digitalWrite(ledG,LOW);
      client.publish(sTopic_K, "0");
  }
}

void setup() {
  Serial.begin(115200);

  // Define pins as output
  pinMode(ledB, OUTPUT);
  pinMode(ledR,OUTPUT);
  pinMode(ledG,OUTPUT);

  Serial.println("Connecting to WiFi...");
  WiFi.begin(WIFI_SSID,WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    digitalWrite(ledB,!digitalRead(ledB));
    delay(1000);
    Serial.print(".");
  }

  client.setServer(MQTT_BROKER,1883);
  client.setCallback(callback);
}

void loop() {
  if (WiFi.status() == WL_CONNECTED && client.connected()) {
    if(digitalRead(ledB)==LOW) {
      digitalWrite(ledB, HIGH);
    }
    checkReset();
    client.loop();
  }
  else {
    digitalWrite(ledB,LOW);
    reconnect();
  }
}