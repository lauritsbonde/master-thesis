#include <SPI.h>
#include "SdFat.h"

void setupLogging(float distance, char* filename) {
  char distanceStr[10];                  // adjust size based on expected float length
  dtostrf(distance, 1, 2, distanceStr);  // (float, minWidth, decimalPlaces, buffer)

  sprintf(filename, "kf-test-%s.csv", distanceStr);

  if (!SD.begin(SD_CS_PIN, SPI_SPEED)) {
    Serial.println("initialization failed!");
    sdLoggingAvailable = false;
    return;
  }

  sdLoggingAvailable = true;
  Serial.println("initialization done.");

  if (SD.exists(filename)) {
    Serial.println("Deleting existing file...");
    SD.remove(filename);
    Serial.println("Done deleting");
  }

  Serial.print("Filename: ");
  Serial.println(filename);

  logFile = SD.open(filename, FILE_WRITE);
  if (logFile) {
    logFile.println("Timestamp (s),Raw-A-0 (m),Raw-A-1 (m),KF-A-0 (m),KF-A-1 (m),MiddlePoint (m),Expected (m), Method, Mode");
    logFile.close();
  } else {
    sdLoggingAvailable = false;
    Serial.println("Failed to create log file.");
  }
}

const char* modeToString(Mode mode) {
  switch (mode) {
    case WARMUP: return "WARMUP";
    case CALIBRATIONMODE: return "CALIBRATION";
    case TESTMODE: return "TEST";
    case UNKNOWN:
    default: return "UNKNOWN";
  }
}

String floatToString(float value, int width = 8, int precision = 6) {
  char buffer[20];
  dtostrf(value, width, precision, buffer);
  return String(buffer);
}

void logDataToSerial(float raw0, float raw1, float d0, float d1, float middle, float expected, const String& method, Mode mode) {
  unsigned long timestamp = millis();
  float timeInSeconds = timestamp / 1000.0;

  Serial.print("DataEntry - "),

  Serial.print("Time: ");
  Serial.print(timeInSeconds);
  Serial.print("s | ");
  Serial.print("Raw0: ");
  Serial.print(raw0);
  Serial.print(" m | Raw1: ");
  Serial.print(raw1);
  Serial.print(" m | ");
  Serial.print("Filtered0: ");
  Serial.print(d0, 6);
  Serial.print(" m | Filtered1: ");
  Serial.print(d1, 6);
  Serial.print(" m | Middle: ");
  Serial.print(middle, 6);
  Serial.print(" m | Expected: ");
  Serial.print(expected, 6);
  Serial.print(" m | Method: ");
  Serial.print(method);
  Serial.print(" | Mode: ");
  Serial.println(modeToString(mode));
}

void logDataAuto(float raw0, float raw1, float d0, float d1, float middle, float expected, const String& method, Mode mode) {
    logDataToSerial(raw0, raw1, d0, d1, middle, expected, method, mode);
}