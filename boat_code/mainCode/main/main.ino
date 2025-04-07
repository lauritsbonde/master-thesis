#include "Communication.h"
#include "CurrentMeasure.h"
#include "SDWriter.h"
#include "MotorControl.h"
#include "LED.h"

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  setupLEDS();

  setupMotors();

  SDWriterSetup();

  setupCommunication();
}

void loop() {
  // put your main code here, to run repeatedly:
  // readEspComm();

  setMotorSpeeds(100);
  delay(2000);
  stopMotors();
  delay(2000);
}
