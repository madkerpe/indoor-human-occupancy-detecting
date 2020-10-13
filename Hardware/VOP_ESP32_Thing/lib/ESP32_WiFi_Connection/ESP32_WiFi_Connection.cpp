#include <ESP32_WiFi_Connection.h>
#include <MLX90640_Shield.h>

// #ifndef VERBOSE_MODE
// #define VERBOSE_MODE
// #endif

int ESP32_WiFiSetup(char* ssid, char* password) {
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(50);
  }

  MLX90640_Shield_WriteByte(WiFi.localIP()[3]);
  return 0;

}

int ESP32_WiFiSetup_verbose(char* ssid, char* password) {
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  MLX90640_Shield_WriteByte(WiFi.localIP()[3]);

  return 0;
}

String ESP32_JsonPacket(float* mlx90640To, uint8_t device_id, uint16_t sequence_id, int8_t mode) {
  
  
  #ifdef VERBOSE_MODE
    Serial.print("Constructing packet ");
    Serial.println(sequence_id);
  #endif

  const size_t json_capacity = JSON_ARRAY_SIZE(32*24) + JSON_OBJECT_SIZE(3) + 21;
  DynamicJsonDocument root(json_capacity);

  root["device_id"] = device_id;
  root["sequence"] = sequence_id;

  JsonArray data = root.createNestedArray("data"); //JsonArray is a smart pointer

  switch (mode) {
    case 0:
      for (int i = 0; i < 768; i++) {
        data.add(mlx90640To[i]);
      } 
      break;
    case 1:
      uint8_t val;
      for (int i = 0; i < 768; i++) {
        if (mlx90640To[i] >= 30) {
          val = 1;
        }
        else {
          val = 0;
        }
      
        data.add(val);
      }
    break;
  }

  String dest;
  serializeJson(root, dest);
 
  #ifdef VERBOSE_MODE
    serializeJsonPretty(root, Serial);
  #endif




return dest;

}

int ESP32_HTTPSetup(HTTPClient http, char* server_ip, uint16_t server_port, char* server_path) {
  http.begin(server_ip, server_port, server_path);
  http.addHeader("Content-Type", "application/json");

  return 0;
}