// CurrentMeasure.cpp
#include "CurrentMeasure.h"
#include <Arduino.h>

bool shallMeasure = false;

String MeasureCurrent() {
  float average = 0;
  for (int i = 0; i < 1000; i++) {
    average = average + (0.0264 * analogRead(A0) - 13.51) / 1000;

    // For 5A mode. If using 20A or 30A mode:
    // 20A: (0.19 * analogRead(A0) - 25)
    // 30A: (0.044 * analogRead(A0) - 3.78)
    delay(1);
  }
  return String(average);
}