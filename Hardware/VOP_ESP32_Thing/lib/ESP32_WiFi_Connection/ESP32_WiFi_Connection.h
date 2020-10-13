#ifndef _ESP32_WiFi_H_
#define _ESP32_WiFi_H_

#include <Wifi.h>
#include <HTTPClient.h>
#include <Arduino.h>
#include <ArduinoJSON.h>

int ESP32_WiFiSetup(char* ssid, char* password);
int ESP32_WiFiSetup_verbose(char* ssid, char* password);
int ESP32_HTTPSetup(HTTPClient http, char* server_ip, uint16_t server_port, char* server_path);

String ESP32_JsonPacket(float* mlx90640To, uint8_t device_id, uint16_t sequence_id, int8_t mode);

#endif