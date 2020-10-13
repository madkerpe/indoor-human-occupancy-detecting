#include <Wire.h>
#include <Arduino.h>
#include <Wifi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

#include <MLX90640_API.h>
#include <MLX90640_I2C_Driver.h>

const byte MLX90640_address = 0x33; //Default 7-bit unshifted address of the MLX90640

const char* ssid = "VOP2.4";
const char* password = "Marijnsuckt";

const char* host = "Thermal sensor 0x33";

const char* rasp_ip = "192.168.1.135"; //"<rasp-ip>/sensor/debug";
const int rasp_port = 5000;
const char* rasp_path = "/sensor/debug";

#define TA_SHIFT 8 //Default shift for MLX90640 in open air
#define PAGE_SIZE 1536 //size of combination of subpages

float mlx90640To[768];
paramsMLX90640 mlx90640;

uint16_t sequence_id = 0;

void setup() {
  Wire.begin();
  Wire.setClock(400000); //Increase I2C clock speed to 400kHz

  Serial.begin(115200); //Fastest serial as possible
  delay(10);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  //Get device parameters - We only have to do this once
  int status;
  uint16_t eeMLX90640[832];
  status = MLX90640_DumpEE(MLX90640_address, eeMLX90640);
  if (status != 0)
    Serial.println("Failed to load system parameters");

  status = MLX90640_ExtractParameters(eeMLX90640, &mlx90640);
  if (status != 0)
    Serial.println("Parameter extraction failed");

  //Once params are extracted, we can release eeMLX90640 array

  //MLX90640_SetRefreshRate(MLX90640_address, 0x02); //Set rate to 2Hz
  //MLX90640_SetRefreshRate(MLX90640_address, 0x03); //Set rate to 4Hz
  MLX90640_SetRefreshRate(MLX90640_address, 0x02); //Set rate to 64Hz
  
}

void loop() {
  //long startTime = millis();
  for (byte i = 0 ; i < 2 ; i++) {
    uint16_t mlx90640Frame[834];
    int status = MLX90640_GetFrameData(MLX90640_address, mlx90640Frame);

    float vdd = MLX90640_GetVdd(mlx90640Frame, &mlx90640);
    float Ta = MLX90640_GetTa(mlx90640Frame, &mlx90640);

    float tr = Ta - TA_SHIFT; //Reflected temperature based on the sensor ambient temperature
    float emissivity = 0.95;

    MLX90640_CalculateTo(mlx90640Frame, &mlx90640, emissivity, tr, mlx90640To);
  }
  //long stopTime = millis();

  HTTPClient http;
  http.begin(rasp_ip, rasp_port, rasp_path);
  http.addHeader("Content-Type", "application/json"); //TODO

  DynamicJsonBuffer jBuffer; //TODO make static
  JsonObject& root = jBuffer.createObject();

  root["device_id"] = MLX90640_address;
  root["sequence"] = sequence_id;
  JsonArray& data = root.createNestedArray("data");
  
  for (uint16_t i = 0; i < 768; i++) {
    data.add(mlx90640To[i]);
  }

  char* jsonRaw = (char*)calloc(sizeof(char), root.measureLength() + 1);
  Serial.println("ROOT MEASURELENGTH");
  Serial.println(root.measureLength());
  
  //root.prettyPrintTo(Serial);
  
  root.printTo(jsonRaw, root.measureLength() + 1);

  int httpResponseCode = http.POST(jsonRaw);
  sequence_id++;

  if (httpResponseCode < 0) {
    Serial.print("Error in sending a POST request, httpResponseCode:");
    Serial.println(httpResponseCode);
   }

  free(jsonRaw);
  http.end();
  
}