#include "MotorControl.h"
#include "SDWriter.h"

ESC leftESC = {Servo(), 9, 12, UNIDIRECTIONAL};
ESC rightESC = {Servo(), 10, 13, UNIDIRECTIONAL};

ESCMode detectESCMode(uint8_t configPin) {
  pinMode(configPin, INPUT_PULLUP);  // pulled HIGH unless grounded
  return digitalRead(configPin) == LOW ? BIDIRECTIONAL : UNIDIRECTIONAL;
}

void setupMotors() {
  leftESC.mode = detectESCMode(leftESC.configPin);
  rightESC.mode = detectESCMode(rightESC.configPin);

  leftESC.servo.attach(leftESC.pwmPin, 1000, 2000);
  rightESC.servo.attach(rightESC.pwmPin, 1000, 2000);

  // Arm ESCs
  leftESC.servo.write(0);
  rightESC.servo.write(0);

  startLogging();
}


void stopMotors() {
  // Stop depends on mode
  int stopValLeft = (leftESC.mode == BIDIRECTIONAL) ? 90 : 0;
  int stopValRight = (rightESC.mode == BIDIRECTIONAL) ? 90 : 0;

  leftESC.servo.write(stopValLeft);
  rightESC.servo.write(stopValRight);

  stopLogging();
}

void setMotorSpeed(ESC& esc, int speed) {
  int pulse;
  if (esc.mode == BIDIRECTIONAL) {
    if(speed < 90) {
      speed = 90;
    }
    pulse = speed;
  } else {
    pulse = speed;
  }

  esc.servo.write(pulse);
}

void setLeftMotorSpeed(int speed) {
  setMotorSpeed(leftESC, speed);
}

void setRightMotorSpeed(int speed) {
  setMotorSpeed(rightESC, speed);
}

void setMotorSpeeds(int speed) {
  setLeftMotorSpeed(speed);
  setRightMotorSpeed(speed);
}