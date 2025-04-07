#include "MotorControl.h"
#include "SDWriter.h"

ESC leftESC = {Servo(), 9, 12, UNIDIRECTIONAL};
ESC rightESC = {Servo(), 10, 13, UNIDIRECTIONAL};

// connected to ground is Bidirectional
ESCMode detectESCMode(uint8_t configPin) {
  pinMode(configPin, INPUT_PULLUP);  // pulled HIGH unless grounded
  return digitalRead(configPin) == LOW ? BIDIRECTIONAL : UNIDIRECTIONAL;
}

ESCModes setupMotors() {
  ESCModes modes;
  modes.left = detectESCMode(leftESC.configPin);
  modes.right = detectESCMode(rightESC.configPin);

  leftESC.mode = modes.left;
  rightESC.mode = modes.right;

  leftESC.servo.attach(leftESC.pwmPin, 1000, 2000);
  rightESC.servo.attach(rightESC.pwmPin, 1000, 2000);

  // Arm esc sequence
  leftESC.servo.write(0);
  rightESC.servo.write(0);

  setMotorSpeeds(180);
  stopMotors();
  // arm done;

  startLogging();

  return modes;
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
  speed = constrain(speed, 0, 180);

  esc.servo.write(speed);
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