#include <Servo.h>

#pragma once

enum ESCMode { BIDIRECTIONAL, UNIDIRECTIONAL };

struct ESC {
  Servo servo;
  uint8_t pwmPin; // signal pin
  uint8_t modePin; // defines directional mode
  uint8_t boostPin; // defines if the esc needs a boost to get started
  ESCMode mode;
  bool needsBoost;
  int speed; // define standard speed for the given ESC;
};

struct ESCModes {
  ESCMode left;
  ESCMode right;
};

ESCModes setupMotors();

void stopMotors();
void setLeftMotorSpeed(int speedPercent);
void setRightMotorSpeed(int speedPercent);
void setMotorSpeeds(int speedPercent);
void StartMotors(int leftMotor, int rightMotor);
void setDefaultSpeeds(int left, int right);
void startDefaultMotors();
