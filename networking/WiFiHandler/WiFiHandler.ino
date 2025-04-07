#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <ArduinoJson.h>

const char* wifiSSID = "Laurits - iPhone";       
const char* wifiPassword = "12345678"; 

unsigned long disconnectStart = 0;
unsigned long lastStatusSend = 0;

ESP8266WebServer wifiServer(80);

ESP8266WiFiClass getWiFi() {
  return WiFi;
}

void setup() {
  Serial.begin(115200);

  WiFi.setAutoReconnect(true);
  WiFi.setSleepMode(WIFI_NONE_SLEEP);
  WiFi.mode(WIFI_STA);
  WiFi.begin(wifiSSID, wifiPassword);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }

  Serial.println();
  Serial.println(WiFi.localIP());

  wifiServer.begin();
}

void loop() {
  wifiServer.handleClient();

  if(WiFi.isConnected() && !mqttClientIsConnected()){
    connectToMqtt();
  }

  if(mqttClientIsConnected()) {
    mqttLoop();
  }

  // Reconnection grace period logic
  bool wifiOk = WiFi.isConnected();
  bool mqttOk = mqttClientIsConnected();

  if (!wifiOk || !mqttOk) {
    if (disconnectStart == 0) {
      disconnectStart = millis();  // Start grace period
    } else if (millis() - disconnectStart > 3000) {
      Serial.println("disconnected");
      disconnectStart = 0;  // Reset timer after reporting
    }
  } else {
    disconnectStart = 0;  // Reset if connection is fine again
  }

  // send status message
  if(millis() - lastStatusSend > 3000){
    if (!wifiOk || !mqttOk) {
      Serial.println("disconnected");// this is listened to by the arduino
    } else {
      Serial.println("ready"); // this is listened to by the arduino
    }
    lastStatusSend = millis();
  }
}