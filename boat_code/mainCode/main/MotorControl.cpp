#include "MotorControl.h"
#include "SDWriter.h"

ESC leftESC = {Servo(), 4, 2, 3, UNIDIRECTIONAL, false, 0}; // mode & boost is change in the setup
ESC rightESC = {Servo(), 5, 6, 7, UNIDIRECTIONAL, false, 0}; // mode & boost is change in the setup

// connected to ground is Bidirectional
ESCMode detectESCMode(uint8_t configPin) {
  pinMode(configPin, INPUT_PULLUP);  // pulled HIGH unless grounded
  return digitalRead(configPin) == LOW ? BIDIRECTIONAL : UNIDIRECTIONAL; // if the configpin is grounded return Biderectional
}

bool detectESCBoost(uint8_t configPin) {
  pinMode(configPin, INPUT_PULLUP);
  return digitalRead(configPin) == LOW ? true : false; 
}

ESCModes setupMotors() {
  ESCModes modes;
  modes.left = detectESCMode(leftESC.modePin);
  modes.right = detectESCMode(rightESC.modePin);

  leftESC.mode = modes.left;
  rightESC.mode = modes.right;

  leftESC.needsBoost = detectESCBoost(leftESC.boostPin);
  rightESC.needsBoost = detectESCBoost(rightESC.boostPin);

  leftESC.servo.attach(leftESC.pwmPin, 1000, 2000);
  rightESC.servo.attach(rightESC.pwmPin, 1000, 2000);

  // Arm esc sequence
  leftESC.servo.write(0);
  rightESC.servo.write(0);

  setMotorSpeeds(180);
  stopMotors();
  // arm done;

  return modes;
}

void setDefaultSpeeds(int left, int right) {
  leftESC.speed = left; 
  rightESC.speed = right; 
}


void stopMotors() {
  // Stop depends on mode
  int stopValLeft = (leftESC.mode == BIDIRECTIONAL) ? 90 : 0;
  int stopValRight = (rightESC.mode == BIDIRECTIONAL) ? 90 : 0;

  leftESC.servo.write(stopValLeft);
  rightESC.servo.write(stopValRight);
  stopLogging();
}

int calculateESCSignal(int speedPercent, ESC esc) {
  speedPercent = constrain(speedPercent, 0, 100);

  if (esc.mode == UNIDIRECTIONAL) {
    // Simple 0–100% to 0–180 signal
    return map(speedPercent, 0, 100, 0, 180);
  }

  // Bidirectional ESC, forward-only
  int stopMax = esc.needsBoost ? 120 : 95;
  return map(speedPercent, 0, 100, stopMax, 180);
}

void setLeftMotorSpeed(int speedPercent) {
  int escSignal = calculateESCSignal(speedPercent, leftESC);
   Serial.print("Set left motor speed to: "); 
   Serial.println(escSignal);
  leftESC.servo.write(escSignal);
}

void setRightMotorSpeed(int speedPercent) {
  int escSignal = calculateESCSignal(speedPercent, rightESC);
  Serial.print("Set right motor speed to: ");
  Serial.println(escSignal);
  rightESC.servo.write(escSignal);
}

void setMotorSpeeds(int speedPercent) {
  setLeftMotorSpeed(speedPercent);
  setRightMotorSpeed(speedPercent);
}

void StartMotors(int leftMotor, int rightMotor) {
    setLeftMotorSpeed(leftMotor);
    setRightMotorSpeed(rightMotor);
    startLogging();
}

void startDefaultMotors() {
  Serial.println("Arduino starting motors");
  StartMotors(leftESC.speed, rightESC.speed);    
}
