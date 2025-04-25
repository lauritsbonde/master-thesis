// Communication.h
#pragma once
#include "MotorControl.h"

struct motorValues {
  int right; 
  int left;
};

void setupCommunication(ESCModes escModes);
char* readEspComm();