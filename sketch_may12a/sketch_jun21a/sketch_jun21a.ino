#include <WiFi.h>
#include <HTTPClient.h>
#include "DHT.h"
#include <esp_task_wdt.h>
#include <ArduinoOTA.h>
#include <ArduinoJson.h>

// ==========================
// WIFI CONFIG
// ==========================
const char* ssid = "OPPO A31";
const char* password = "12345678";

// ==========================
// API CONFIG
// ==========================
const char* serverUrl = "http://10.205.198.79:8000/iot/update";
const char* deviceToken = "CHANGE_ME_TO_YOUR_DEVICE_INGEST_SECRET"; // matches DEVICE_INGEST_SECRET on server, leave empty "" if not set

// ==========================
// BIN IDENTITY (change per physical device)
// ==========================
const int BIN_ID = 1;
const char* BIN_LOCATION = "Smart bin node 1";
const float BIN_LATITUDE = 23.2599;
const float BIN_LONGITUDE = 77.4126;
const char* BIN_ZONE = "FIELD";

// ==========================
// PIN CONFIG
// ==========================
#define TRIG_PIN 14
#define ECHO_PIN 15
#define GAS_PIN 34
#define BATTERY_PIN 35

#define DHTPIN 12
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

// ==========================
// BIN CONFIG
// ==========================
const int BIN_HEIGHT_CM = 30;

// ==========================
// TIMING (non-blocking loop)
// ==========================
const unsigned long SEND_INTERVAL_MS = 5000;
unsigned long lastSendTime = 0;

// ==========================
// RETRY CONFIG
// ==========================
const int MAX_HTTP_RETRIES = 2;

// ==========================
// SETUP
// ==========================
void connectWiFi() {
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);

  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    esp_task_wdt_reset();
    // Avoid hanging forever if WiFi never comes up
    if (millis() - start > 30000) {
      Serial.println("\nWiFi connect timeout, retrying...");
      WiFi.disconnect();
      WiFi.begin(ssid, password);
      start = millis();
    }
  }
  Serial.println("\nWiFi Connected!");
  Serial.print("Device IP: ");
  Serial.println(WiFi.localIP());
}

void setup() {
  Serial.begin(115200);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  dht.begin();

  Serial.println("\n=================================");
  Serial.println("CleanCity AI Hardware Node");
  Serial.println("=================================");

  esp_task_wdt_config_t wdt_config = {
    .timeout_ms = 60000,
    .idle_core_mask = 0,
    .trigger_panic = true
    };
  esp_task_wdt_init(&wdt_config);
  esp_task_wdt_add(NULL); // current task ko watchdog mein register karo

  connectWiFi();

  ArduinoOTA.setHostname("cleancity-bin-1");
  ArduinoOTA.onStart([]() { Serial.println("[OTA] Start"); });
  ArduinoOTA.onEnd([]() { Serial.println("[OTA] End"); });
  ArduinoOTA.onError([](ota_error_t e) { Serial.printf("[OTA] Error %u\n", e); });
  ArduinoOTA.begin();
  Serial.println("ArduinoOTA ready (same LAN as IDE for upload).");
}

// ==========================
// ULTRASONIC FUNCTION (with timeout, returns -1 on sensor failure)
// ==========================
float getDistanceCM() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);

  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);

  digitalWrite(TRIG_PIN, LOW);

  // 30ms timeout (~5m max range) prevents indefinite blocking
  long duration = pulseIn(ECHO_PIN, HIGH, 30000UL);

  if (duration == 0) {
    return -1.0; // sensor error / no echo received
  }

  return duration * 0.034 / 2;
}

// ==========================
// SEND TELEMETRY WITH RETRY
// ==========================
bool sendTelemetry(const String& payload) {
  for (int attempt = 1; attempt <= MAX_HTTP_RETRIES; attempt++) {
    esp_task_wdt_reset();

    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    if (strlen(deviceToken) > 0) {
      http.addHeader("X-Device-Token", deviceToken);
    }
    http.setTimeout(5000);

    Serial.println("\n=================================");
    Serial.printf("Sending Telemetry (attempt %d/%d)...\n", attempt, MAX_HTTP_RETRIES);
    Serial.println(payload);

    int httpResponseCode = http.POST(payload);
    Serial.print("HTTP Response Code: ");
    Serial.println(httpResponseCode);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Server Response:");
      Serial.println(response);
      http.end();
      return true;
    } else {
      Serial.printf("Send failed (code %d), %s\n", httpResponseCode,
                     attempt < MAX_HTTP_RETRIES ? "retrying..." : "giving up.");
      http.end();
      delay(500);
    }
  }
  return false;
}

// ==========================
// LOOP (non-blocking)
// ==========================
void loop() {
  esp_task_wdt_reset();
  ArduinoOTA.handle();

  // WiFi auto-reconnect
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi Disconnected! Reconnecting...");
    connectWiFi();
    return;
  }

  unsigned long now = millis();
  if (now - lastSendTime < SEND_INTERVAL_MS) {
    return; // not time yet, loop again without blocking
  }
  lastSendTime = now;

  // ==========================
  // READ ULTRASONIC
  // ==========================
  float distance = getDistanceCM();
  int fillLevel;
  bool ultrasonicOk = (distance >= 0);

  if (!ultrasonicOk) {
    Serial.println("Ultrasonic sensor error - no echo received");
    fillLevel = -1; // signal sensor failure to backend, do NOT report false 100%
  } else {
    fillLevel = 100 - ((distance / BIN_HEIGHT_CM) * 100);
    fillLevel = constrain(fillLevel, 0, 100);
  }

  // ==========================
  // READ GAS SENSOR
  // ==========================
  int gasRaw = analogRead(GAS_PIN);
  int gasLevel = map(gasRaw, 0, 4095, 0, 100);

  // ==========================
  // READ DHT
  // ==========================
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  bool dhtOk = !(isnan(temperature) || isnan(humidity));
  if (!dhtOk) {
    Serial.println("DHT Sensor Error!");
    temperature = 0;
    humidity = 0;
  }

  // ==========================
  // BATTERY
  // ==========================
  int adcBat = analogRead(BATTERY_PIN);
  int battery = constrain(map(adcBat, 1860, 2600, 0, 100), 0, 100);

  // ==========================
  // JSON PAYLOAD (ArduinoJson - safe serialization)
  // ==========================
  StaticJsonDocument<384> doc;
  doc["bin_id"] = BIN_ID;
  doc["location"] = BIN_LOCATION;
  doc["latitude"] = BIN_LATITUDE;
  doc["longitude"] = BIN_LONGITUDE;
  doc["zone"] = BIN_ZONE;
  doc["fill_level"] = fillLevel;
  doc["gas_level"] = gasLevel;
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  doc["battery"] = battery;
  doc["sensor_ok"] = ultrasonicOk && dhtOk;

  String jsonPayload;
  serializeJson(doc, jsonPayload);

  // ==========================
  // SEND
  // ==========================
  sendTelemetry(jsonPayload);
}