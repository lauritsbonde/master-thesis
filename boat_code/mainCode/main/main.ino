#include "Communication.h"
#include "CurrentMeasure.h"
#include "SDWriter.h"
#include "MotorControl.h"
#include "LED.h"

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  setupLEDS();

  ESCModes escModes = setupMotors();

  SDWriterSetup();

  setupCommunication(escModes);
}

void loop() {
  // put your main code here, to run repeatedly:
  readEspComm();


}
