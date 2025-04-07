#include <Servo.h>

#pragma once

enum ESCMode { BIDIRECTIONAL, UNIDIRECTIONAL };

struct ESC {
  Servo servo;
  uint8_t pwmPin;
  uint8_t configPin;
  ESCMode mode;
};

void setupMotors();

void stopMotors();
void setLeftMotorSpeed(int speed);
void setRightMotorSpeed(int speed);
void setMotorSpeeds(int speed);