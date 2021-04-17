#include "OV2640.h"
#include <WiFi.h>
#include <WebServer.h>
#include <WiFiClient.h>
#include "SimStreamer.h"

#include <WiFiUdp.h>

OV2640 cam;
WebServer server(80);
WiFiUDP udp;
WiFiClient client;

const char* WIFI_SSID = "FPA-OpenCV";
const char* WIFI_PASS = "BoeckBoeck";
const char * udpAddress = "10.0.60.1";
const int udpPort = 44444;

String CAM_NAME = "ESP32-CAM";

camera_config_t camera_config{

    .pin_pwdn = 32,
    .pin_reset = -1,

    .pin_xclk = 0,

    .pin_sscb_sda = 26,
    .pin_sscb_scl = 27,

    // Note: LED GPIO is apparently 4 not sure where that goes
    // per https://github.com/donny681/ESP32_CAMERA_QR/blob/e4ef44549876457cd841f33a0892c82a71f35358/main/led.c
    .pin_d7 = 35,
    .pin_d6 = 34,
    .pin_d5 = 39,
    .pin_d4 = 36,
    .pin_d3 = 21,
    .pin_d2 = 19,
    .pin_d1 = 18,
    .pin_d0 = 5,
    .pin_vsync = 25,
    .pin_href = 23,
    .pin_pclk = 22,
    .xclk_freq_hz = 20000000,
    .ledc_timer = LEDC_TIMER_1,
    .ledc_channel = LEDC_CHANNEL_1,
    .pixel_format = PIXFORMAT_JPEG,
    // .frame_size = FRAMESIZE_UXGA, // needs 234K of framebuffer space
    // .frame_size = FRAMESIZE_SXGA, // needs 160K for framebuffer
    // .frame_size = FRAMESIZE_XGA, // needs 96K or even smaller FRAMESIZE_SVGA - can work if using only 1 fb
    .frame_size = FRAMESIZE_XGA,
    .jpeg_quality = 10, //0-63 lower numbers are higher quality
    .fb_count = 2       // if more than one i2s runs in continous mode.  Use only with jpeg
};

void handle_jpg_stream(void)
{
    WiFiClient client = server.client();
    String response = "HTTP/1.1 200 OK\r\n";
    response += "Content-Type: multipart/x-mixed-replace; boundary=frame\r\n\r\n";
    server.sendContent(response);

    while (1)
    {
        cam.run();
        if (!client.connected())
            break;
        response = "--frame\r\n";
        response += "Content-Type: image/jpeg\r\n\r\n";
        server.sendContent(response);

        client.write((char *)cam.getfb(), cam.getSize());
        server.sendContent("\r\n");
        if (!client.connected())
            break;
    }
}

void setup()
{
    Serial.begin(115200);
    while (!Serial)
    {
        ;
    }

    int camInit =
    cam.init(camera_config);
    Serial.printf("Camera init returned %d\n", camInit);

    IPAddress ip;

    WiFi.persistent(false);
    WiFi.mode(WIFI_MODE_STA);
    //WiFi.setHostname("FACECAM");
    WiFi.begin(WIFI_SSID, WIFI_PASS);


    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(F("."));
    }
    ip = WiFi.localIP();
    Serial.println(F("WiFi connected"));
    Serial.println(ip);

    
    // initialize udp and transfer buffer
    unsigned int length = CAM_NAME.length()+1;
    udp.begin(udpPort);
    uint8_t buffer[length];
    CAM_NAME.getBytes(buffer, length);

    // send name of camera to server
    udp.beginPacket(udpAddress, udpPort);
    udp.write(buffer, 16);
    udp.endPacket();
    memset(buffer, 0, 50);

    // start http-server
    server.on("/", HTTP_GET, handle_jpg_stream);
    server.begin();
}

CStreamer *streamer;

void loop()
{
  server.handleClient();
}