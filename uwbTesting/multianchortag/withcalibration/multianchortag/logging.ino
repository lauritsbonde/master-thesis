#include <SPI.h>
#include "SdFat.h"

void setupLogging(float distance, char* filename) {
  char distanceStr[10];  // adjust size based on expected float length
  dtostrf(distance, 1, 2, distanceStr);  // (float, minWidth, decimalPlaces, buffer)

  sprintf(filename, "multi-uwb-test-calibrated-%s.csv", distanceStr);

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
    logFile.println("Timestamp (s),Anchor-0 (m),Anchor-1 (m),MiddlePoint (m),Expected (m), Method, Mode");
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

void printFloatToFile(FsFile& file, float value, int width = 8, int precision = 6) {
  char buffer[20];
  dtostrf(value, width, precision, buffer);
  file.print(buffer);
}

void logDataToFile(float d0, float d1, float middle, float expected, const String& method, Mode mode) {
  logFile = SD.open(filename, FILE_WRITE);
  if (logFile) {
    
    unsigned long timestamp = millis();
    printFloatToFile(logFile, timestamp / 1000.0, 6, 2); logFile.print(",");
    printFloatToFile(logFile, d0); logFile.print(",");
    printFloatToFile(logFile, d1); logFile.print(",");
    printFloatToFile(logFile, middle); logFile.print(",");
    printFloatToFile(logFile, expected); logFile.print(",");
    logFile.print(method); logFile.print(",");
    logFile.println(modeToString(mode));

    logFile.close();
  } else {
    Serial.println("Failed to write to SD card!");
  }
}

void logDataToSerial(float d0, float d1, float middle, float expected, const String& method, Mode mode) {
  unsigned long timestamp = millis();
  float timeInSeconds = timestamp / 1000.0;

  Serial.print("Time: "); Serial.print(timeInSeconds); Serial.print("s | ");
  Serial.print("Anchor 0: "); Serial.print(d0); Serial.print(" m | ");
  Serial.print("Anchor 1: "); Serial.print(d1); Serial.print(" m | ");
  Serial.print("Middle: "); Serial.print(middle); Serial.print(" m | ");
  Serial.print("Expected: "); Serial.print(expected); Serial.print(" m | ");
  Serial.print("Method: "); Serial.print(method); Serial.print(" | ");
  Serial.print("Mode: "); Serial.println(modeToString(mode));
}

void logDataAuto(float d0, float d1, float middle, float expected, const String& method, Mode mode) {
  if (sdLoggingAvailable) {
    logDataToFile(d0, d1, middle, expected, method, mode);
  } else {
    logDataToSerial(d0, d1, middle, expected, method, mode);
  }
}