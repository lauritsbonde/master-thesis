#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <ArduinoJson.h>

const char* wifiSSID = "Laurits - iPhone";       
const char* wifiPassword = "12345678"; 

ESP8266WebServer wifiServer(80);

void setupWiFi() {
  Serial.begin(115200);
  Serial.println("Starting Wi-Fi...");

  WiFi.setAutoReconnect(true);
  WiFi.setSleepMode(WIFI_NONE_SLEEP);
  WiFi.mode(WIFI_STA);
  WiFi.begin(wifiSSID, wifiPassword);

  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.print("Connected to WiFi! IP address: ");
  Serial.println(WiFi.localIP());

  wifiServer.begin();
  Serial.println("Web server started");
}

void handleWiFiRequests() {
  wifiServer.handleClient();
}