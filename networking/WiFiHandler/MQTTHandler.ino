#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>
// This file also uses functions defined in the wifiHandler.ino - they are automatically concatinated


/******* MQTT Broker Connection Details *******/
const char* mqtt_server = "ca403c7db33f468fbc8fa41f694c6f4d.s1.eu.hivemq.cloud";
const char* mqtt_username = "nicklasjeppesen";
const char* mqtt_password = "Xujme3-zefrid-reqjyq";
const int mqtt_port = 8883;

const char* subscribeTopics[] = {"boats/motors", "boats/motorSetup", "boats/motors-start", "boats/motorsCalibration"};
const int numTopics = 4; // this is the length of the array above

/**** Secure WiFi Connectivity Initialisation *****/
WiFiClientSecure espClient;

/**** MQTT Client Initialisation Using WiFi Connection *****/
PubSubClient client(espClient);

bool mqttClientIsConnected(){
  return client.connected();
}

void mqttLoop(){
  client.loop();
}

/************* Connect to MQTT Broker ***********/
void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "ESP8266Client-";   // Create a random client ID
    clientId += getWiFi().macAddress();
    // Attempt to connect
    if (client.connect(clientId.c_str(), mqtt_username, mqtt_password)) {
      Serial.println("ready");

      for(int i = 0; i < numTopics; i++){
        client.subscribe(subscribeTopics[i]);   // subscribe the topics here
      }

    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");   // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

/************* These functions will only get called on messages from others ***********/
void handleInstruction(JsonDocument doc) {
  Serial.println("Instruction received:");

  if (doc.containsKey("leftMotor") && doc.containsKey("rightMotor")) {
    int left = doc["leftMotor"];
    int right = doc["rightMotor"];
    Serial.print("left: ");
    Serial.print(left);
    Serial.print(" - right: ");
    Serial.println(right);
  } else {
    Serial.println("Missing keys in instruction.");
  }
}

void handleSpeedSetup(JsonDocument doc) {
  Serial.println("Instruction received:");


  if (doc.containsKey("leftMotor") && doc.containsKey("rightMotor") && doc.containsKey("mac")) {
    int left = doc["leftMotor"];
    int right = doc["rightMotor"];
    const char* mac = doc["mac"];
    if(strcmp(mac, getWiFi().macAddress().c_str()) == 0) {
      Serial.print("setup ");
      Serial.print("left: ");
      Serial.print(left);
      Serial.print(" - right: ");
      Serial.println(right);
    }
  } else {
    Serial.println("Missing keys in instruction.");
  }
}

void handleStartMotor() {
  Serial.println("startMotor");
}

void  handleMotorCalibration(JsonDocument doc) {

  if (doc.containsKey("leftMotor") && doc.containsKey("rightMotor") && doc.containsKey("mac")) {
    int left = doc["leftMotor"];
    int right = doc["rightMotor"];
    const char* mac = doc["mac"];
    if(strcmp(mac, getWiFi().macAddress().c_str()) == 0) {
      Serial.print("calibration ");
      Serial.print("left: ");
      Serial.print(left);
      Serial.print(" - right: ");
      Serial.println(right);
    }
  } else {
    Serial.println("Missing keys in instruction.");
  }

}

/**** Function to handle incoming messages *****/
void callback(char* topic, byte* payload, unsigned int length) {
  // Create a StaticJsonDocument with a sufficient size for your JSON message
  StaticJsonDocument<256> doc;

  // Attempt to deserialize the JSON from the payload
  DeserializationError error = deserializeJson(doc, payload, length);

  // Check if deserialization was successful
  if (error) {
    return;
  }

  // check that the message is not from self
  String mac = doc["MAC"];
  if(strcmp(mac.c_str(), getWiFi().macAddress().c_str()) == 0) {
    return;
  }

  if(strcmp(topic, "boats/motors") == 0) {
    handleInstruction(doc);
  } else if(strcmp(topic, "boats/motorSetup") == 0) {
    handleSpeedSetup(doc);
  } else if(strcmp(topic, "boats/motors-start") == 0) {
   handleStartMotor();
  } else if (strcmp(topic, "boats/motorsCalibration") == 0) {
    handleMotorCalibration(doc);
  }

}

/**** Method for Publishing MQTT Messages **********/
void publishMessage(const char* topic, JsonDocument doc , boolean retained){
  String jsonString;
  doc["MAC"] = getWiFi().macAddress();
  serializeJson(doc, jsonString);
  client.publish(topic, jsonString.c_str(), retained);
}

/*** Methods for Game Messages ****/
void connected(ESCModes escModes) {
  JsonDocument doc;

  doc["message"] = "connected";
  doc["leftMode"] = escModes.left;
  doc["rightMode"] = escModes.right;

  publishMessage("connected", doc, false);
}

void connectToMqtt(ESCModes escModes) {
  espClient.setInsecure();

  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  int timeOut = 0;

  while(!client.connected() && timeOut < 10) {
    reconnect();
    timeOut++;
  }

  connected(escModes);
}
