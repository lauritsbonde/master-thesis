#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>
// This file also uses functions defined in the wifiHandler.ino - they are automatically concatinated


/******* MQTT Broker Connection Details *******/
const char* mqtt_server = "92cb876ba5c6470baaadb3f0ae70e2b8.s1.eu.hivemq.cloud";
const char* mqtt_username = "lauritsbonde";
const char* mqtt_password = "rzF1@2E&XZ$nUpTQTQ3z";
const int mqtt_port =8883;

const char* subscribeTopics[] = {"connect", "move", "selectedPiece", "startNumber"};
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
      Serial.println("connected");

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
void handleSelectedPiece(JsonDocument doc){
  int oppPlays = doc["selected"];
  if(oppPlays == Cross) {
    setOppPiece(Cross);
  } else if(oppPlays == Circle){
    setOppPiece(Circle);
  } else {
    Serial.println("Unknown piece");
  }
}

void handleWhoStartsMessage(JsonDocument doc) {
  long oppRandNum = doc["randLong"];

  Serial.print("oppRandomNum: ");
  Serial.println(oppRandNum);

  decideWhoStarts(oppRandNum); // gameHandler.ino function
}

void handleMove(JsonDocument doc){
  int row = doc["row"];
  int col = doc["col"];

  placeOppPiece(row, col); // gameHandler.ino function
}

/**** Function to handle incoming messages *****/
void callback(char* topic, byte* payload, unsigned int length) {
  // Create a StaticJsonDocument with a sufficient size for your JSON message
  StaticJsonDocument<256> doc;
  
  // Attempt to deserialize the JSON from the payload
  DeserializationError error = deserializeJson(doc, payload, length);
  
  // Print the topic
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("]: ");
  
  // Check if deserialization was successful
  if (error) {
    Serial.print("deserializeJson() failed: ");
    Serial.println(error.f_str());
    return;
  }

  // check that the message is not from self
  String mac = doc["MAC"];
  if(strcmp(mac.c_str(), getWiFi().macAddress().c_str()) == 0) {
    Serial.println("Own message");
    return;
  }

  Serial.print("topic: ");
  Serial.println(topic);

  if(strcmp(topic, "selectedPiece") == 0) {
    Serial.println("handling Piece selection");
    handleSelectedPiece(doc);
  } else if(strcmp(topic, "startNumber") == 0) {
    Serial.println("handling who starts");
    handleWhoStartsMessage(doc);
  } else if(strcmp(topic, "move") == 0) {
    Serial.println("Handling move");
    handleMove(doc);
  } else {
    Serial.println("Something went wrong");
  }
}

/**** Method for Publishing MQTT Messages **********/
void publishMessage(const char* topic, JsonDocument doc , boolean retained){
  String jsonString;
  doc["MAC"] = getWiFi().macAddress();
  serializeJson(doc, jsonString);
  if (client.publish(topic, jsonString.c_str(), retained)) {
    Serial.println("Message publised ["+String(topic)+"]: "+jsonString);
  } else {
    Serial.println("Message publish failed");
  }
}

/*** Methods for Game Messages ****/
void connected(){
  JsonDocument doc;

  // Assign values to the JSON document
  doc["message"] = "connected";

  // Create a String object to hold the serialized JSON
  publishMessage("connected", doc, false);
}

void sendSelectPieceMessage(int piece) {
  JsonDocument doc;

  // Assign values to the JSON document
  doc["selected"] = piece;
  
  publishMessage("selectedPiece", doc, false);
}

void sendRandomNumber(long randomNum) {
  JsonDocument doc;

  doc["randLong"] = randomNum;

  publishMessage("startNumber", doc, false);
}

void sendMove(int row, int col) {
  JsonDocument doc;
  doc["row"] = row;
  doc["col"] = col;

  publishMessage("move", doc, false);
}

void connectToMqtt() {
  espClient.setInsecure();

  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  int timeOut = 0;

  while(!client.connected() && timeOut < 10) {
    reconnect();
    timeOut++;
  }

  JsonDocument doc;
  doc["message"] = "Connected";

  publishMessage("connected", doc, false);
}

