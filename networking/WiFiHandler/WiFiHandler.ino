#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <ArduinoJson.h>

const char* wifiSSID = "Nicklas jeppesen";
const char* wifiPassword = "12345678";

unsigned long disconnectStart = 0;
unsigned long lastStatusSend = 0;

enum ESCMode { BIDIRECTIONAL, UNIDIRECTIONAL };
struct ESCModes {
  ESCMode left;
  ESCMode right;
};

ESCModes escModes;
bool modesReceived = false;

ESP8266WebServer wifiServer(80);

ESP8266WiFiClass getWiFi() {
  return WiFi;
}

void readESCModeMessage() {
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');

    int leftStart = line.indexOf("leftMode: ");
    int rightStart = line.indexOf("rightMode: ");

    if (leftStart != -1 && rightStart != -1) {
      int leftValue = line.substring(leftStart + 10, line.indexOf(" -")).toInt();
      int rightValue = line.substring(rightStart + 11).toInt();

      escModes.left = (ESCMode)leftValue;
      escModes.right = (ESCMode)rightValue;
      modesReceived = true;

      Serial.print("Received ESC modes - Left: ");
      Serial.print(escModes.left == BIDIRECTIONAL ? "BIDIRECTIONAL" : "UNIDIRECTIONAL");
      Serial.print(", Right: ");
      Serial.println(escModes.right == BIDIRECTIONAL ? "BIDIRECTIONAL" : "UNIDIRECTIONAL");
    }
  }
}
void setup() {
  Serial.begin(115200);
  Serial.println("Starting ESP setup");

  while (!modesReceived) {
    readESCModeMessage();
    delay(10);
  }

  WiFi.setAutoReconnect(true);
  WiFi.setSleepMode(WIFI_NONE_SLEEP);
  WiFi.mode(WIFI_STA);
  WiFi.begin(wifiSSID, wifiPassword);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("try to connect to Wifi");
  }

  Serial.println();
  Serial.println(WiFi.localIP());

  wifiServer.begin();
}

void loop() {
  wifiServer.handleClient();

  if(WiFi.isConnected() && !mqttClientIsConnected()){
    connectToMqtt(escModes);
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
