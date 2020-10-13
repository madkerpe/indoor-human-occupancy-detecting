// #ifndef VERBOSE_MODE
// #define VERBOSE_MODE
// #endif

#include <stdint.h>
#include <Wire.h>

#include <MLX90640_API.h>
#include <ESP32_WiFi_Connection.h>
#include <MLX90640_Shield.h>
#include <ArduinoJson.h>

#define DEFAULT_FPS 4
#define DEFAULT_SSID "VOP2.4"
#define DEFAULT_PASS "Marijnsuckt"

#define DEFAULT_SERVER_IP "192.168.1.31"
#define DEFAULT_SERVER_PATH "/sensor/debug"
#define DEFAULT_SERVER_PORT 5000

#define DEFAULT_SERIAL_SPEED 400000
#define DEFAULT_I2C_SPEED 115200

#define DEFAULT_DEVICE_ID 36
#define MLX_I2C_ADDR 0x33

#define VERBOSE_MODE 1

#include <chrono>
#include <thread>

//Variables for the setup
uint16_t eeMLX90640[832];
paramsMLX90640 mlx90640;

//variables for the routine function
uint16_t frame[834];
uint16_t sequence_id = 0;
float mlx90640To[768];
float eTa;

HTTPClient http;
String jsonRaw;

#ifdef VERBOSE_MODE
  int httpResponseCode;
#endif

static std::chrono::microseconds frame_time;

void setup() {
  Wire.begin();
  Wire.setClock(400000);

  #ifdef VERBOSE_MODE
    Serial.begin(115200);
    delay(10);
  #endif

  MLX90640_FullSetup(MLX_I2C_ADDR, DEFAULT_FPS, eeMLX90640, &mlx90640);
  MLX90640_Shield_setup();
  frame_time = std::chrono::microseconds(1000000/(4*DEFAULT_FPS) + 850);
  
  char* ssid = DEFAULT_SSID;
  char* password = DEFAULT_PASS;
  
  #ifdef VERBOSE_MODE
    delay(10);
    ESP32_WiFiSetup_verbose(ssid, password);
  #else
    ESP32_WiFiSetup(ssid, password);
  #endif
}

void loop() {

  auto start = std::chrono::system_clock::now();

  MLX90640_GetFrameTo(MLX_I2C_ADDR, frame, eeMLX90640, &mlx90640, 1, mlx90640To);
  jsonRaw = ESP32_JsonPacket(mlx90640To, DEFAULT_DEVICE_ID, sequence_id, 0);
  sequence_id++;

  http.begin(DEFAULT_SERVER_IP, DEFAULT_SERVER_PORT, DEFAULT_SERVER_PATH);
  http.addHeader("Content-Type", "application/json");

  #ifdef VERBOSE_MODE
    int httpResponseCode = http.POST(jsonRaw);

    if (httpResponseCode) {
      Serial.print("POST request, httpResponseCode:");
      Serial.println(httpResponseCode);
    }

  #else
    http.POST(jsonRaw);
  #endif

  http.end(); // TODO is this neccesary, can't we just set up one http connection?

  auto end = std::chrono::system_clock::now();
  auto elapsed = std::chrono::duration_cast<std::chrono::microseconds>(end - start);

  std::this_thread::sleep_for(std::chrono::microseconds(frame_time - elapsed));
}