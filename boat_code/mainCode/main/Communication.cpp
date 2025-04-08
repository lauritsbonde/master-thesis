// Communication.cpp
#include <Arduino.h>
#include "Communication.h"
#include "MotorControl.h"
#include "LED.h"

bool espConnected = false;

void setupCommunication(ESCModes escModes) {
  Serial2.begin(115200);
  espNotReady();
  
  // write the modes to the esp
  Serial2.print("leftMode: ");
  Serial2.print(escModes.left);
  Serial2.print(" - rightMode: ");
  Serial2.println(escModes.right);

  delay(250);
}

char* readEspComm() {
  static String receivedData = "";
  static unsigned long lastReadTime = 0;
  const unsigned long readInterval = 50;

  if (millis() - lastReadTime > readInterval) {
    lastReadTime = millis();

    while (Serial2.available()) {
      char c = Serial2.read();

      if (c == '\n' && receivedData.length() > 0) {
        //check if the message contains disconnected
        if(receivedData.indexOf("disconnected") >= 0){
          Serial.println("stopping motors");
          stopMotors();
          receivedData = "";
          espConnected = false;
          espNotReady();
          return;
        }

        if(receivedData.indexOf("ready") >= 0){
          Serial.println("ESP is ready");
          receivedData = "";
          espConnected = true;
          espReady();
          return;
        }

        // Parse the values (percentages)
        int rightVal = 0;
        int leftVal = 0;

        int rightIndex = receivedData.indexOf("right:");
        int leftIndex = receivedData.indexOf("left:");

        if (rightIndex != -1 && leftIndex != -1) {
          // Extract number after "right:"
          String rightStr = receivedData.substring(rightIndex + 6, receivedData.indexOf("-", rightIndex));
          rightStr.trim();
          rightVal = rightStr.toInt();

          // Extract number after "left:"
          String leftStr = receivedData.substring(leftIndex + 5);
          leftStr.trim();
          leftVal = leftStr.toInt();

          if(espConnected){
            if(leftVal == 0 && rightVal == 0){
              stopMotors();
              motorStop();
            } else {
              setLeftMotorSpeed(leftVal);
              setRightMotorSpeed(rightVal);
              motorRuns();
            }
          }
        } else {
          Serial.print("Malformed message: ");
          Serial.println(receivedData);
        }

        receivedData = "";
      } else {
        receivedData += c;
      }
    }
  }

  return (char*)receivedData.c_str(); // You can ignore the return if you're parsing inline
}