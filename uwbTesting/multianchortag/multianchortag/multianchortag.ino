#include <SPI.h>
#include "SdFat.h"

SdFat SD;
#define SD_CS_PIN SS
#define SPI_SPEED SD_SCK_MHZ(4)

int distance = 30; // Tag height in cm
FsFile logFile;
char filename[32];
bool sdLoggingAvailable = false;

float baseLength = 0.184; // In meters

float distanceFromTopToAnchor(float baseCm, float heightCm) {
  float halfBase = baseCm / 2.0;
  return sqrt(halfBase * halfBase + heightCm * heightCm);
}

float expected = distanceFromTopToAnchor(baseLength * 100.0f, distance); // cm -> m

void setupLogging() {
  sprintf(filename, "multi-uwb-test-%dcm.csv", distance);

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
  }

  logFile = SD.open(filename, FILE_WRITE);
  if (logFile) {
    logFile.println("Timestamp (s), Anchor-0 (m), Anchor-1 (m), MiddlePoint (m), Expected (m), Method");
    logFile.close();
  } else {
    sdLoggingAvailable = false;
    Serial.println("Failed to create log file.");
  }
}

void setup() {
  Serial.begin(9600);
  
  setupLogging();

  Serial1.begin(115200);
  delay(500);

  const char *commands[] = {
    "AT+RST",
    "AT+anchor_tag=0,0",
    "AT+interval=5",
    "AT+switchdis=1"
  };

  for (const char* cmd : commands) {
    Serial.print("Sending: ");
    Serial.println(cmd);
    Serial1.println(cmd);
    delay(200);
  }

  Serial.println("Everything is setup!");
}

void loop() {
  static String receivedData = "";
  static unsigned long lastReadTime = 0;
  const unsigned long readInterval = 100;
  static float distances[2] = { NAN, NAN };

  if (millis() - lastReadTime > readInterval) {
    lastReadTime = millis();
    while (Serial1.available()) {
      char c = Serial1.read();
      if (c == '\n') {
        float distanceVal = extractDistance(receivedData);
        int deviceId = extractAnchorDevice(receivedData);

        if (!isnan(distanceVal) && deviceId >= 0 && deviceId < 2) {
          distances[deviceId] = distanceVal;

          if (!isnan(distances[0]) && !isnan(distances[1])) {
            String method;
            float dm;

            bool violatesTriangle = (
              distances[0] + distances[1] <= baseLength ||
              fabs(distances[0] - distances[1]) >= baseLength
            );

            if (violatesTriangle) {
              Serial.println("Triangle inequality violated");
              method = "estimate";
              dm = trilaterationEstimate(distances[0], distances[1], baseLength);
              if (dm == 0.0f) {
                method = "fallback";
                dm = trilaterationFallback(distances[0], distances[1]);
              }
            } else {
              dm = trilaterationHeight(distances[0], distances[1], baseLength);
              if (dm < 0.0f) { // check for geometry failure
                Serial.println("Direct method failed due to invalid triangle geometry");
                method = "estimate";
                dm = trilaterationEstimate(distances[0], distances[1], baseLength);
                if (dm == 0.0f) {
                  method = "fallback";
                  dm = trilaterationFallback(distances[0], distances[1]);
                }
              } else {
                method = "direct";
              }
            }

            logDataAuto(distances[0], distances[1], dm, expected / 100.0f, method);
          }
        } else {
          Serial.println("invalid distances");
        }

        receivedData = "";
      } else {
        receivedData += c;
      }
    }
  }

  if (millis() - lastReadTime > 2000) {
    Serial.println("Serial1 not available");
    lastReadTime = millis();
  }
}

int extractAnchorDevice(String input) {
  if (input.startsWith("an")) {
    int colonIndex = input.indexOf(':');
    if (colonIndex != -1) {
      return input.substring(2, colonIndex).toInt();
    }
  }
  return -1;
}

float extractDistance(String input) {
  int startIndex = input.indexOf(':');
  if (startIndex != -1) {
    String numPart = input.substring(startIndex + 1);
    numPart.trim();
    return numPart.toFloat();
  }
  return NAN;
}

float trilaterationHeight(float d0, float d1, float base) {
  float x = (d0 * d0 - d1 * d1) / (2.0f * base);
  if (fabs(x) > base / 2.0f) {
    Serial.println("x is outside base: invalid triangle geometry");
    return -1.0f;
  }
  float ySquared = d0 * d0 - x * x;

  if (ySquared < 0.0f) {
    Serial.println("Invalid geometry: negative y²");
    return -1.0f;
  }
  return sqrt(ySquared);
}

float trilaterationEstimate(float d0, float d1, float base) {
  float a = min(d0, d1);
  float b = max(d0, d1);
  float x = (a * a - b * b) / (2.0f * base);
  float ySquared = a * a - x * x;

  if (ySquared < 0.0f) {
    Serial.println("Even fallback estimate failed: negative y²");
    ySquared = 0.0f;
  }
  return sqrt(ySquared);
}

float trilaterationFallback(float d0, float d1) {
  float minD = min(d0, d1);
  Serial.println("Using fallback vertical estimate based on min(d0, d1): ");
  return minD;
}

void logDataToSerial(float d0, float d1, float middle, float expected, const String& method) {
  unsigned long timestamp = millis();
  float timeInSeconds = timestamp / 1000.0;

  Serial.print("Time: "); Serial.print(timeInSeconds, 2); Serial.print("s | ");
  Serial.print("Anchor 0: "); Serial.print(d0, 3); Serial.print(" m | ");
  Serial.print("Anchor 1: "); Serial.print(d1, 3); Serial.print(" m | ");
  Serial.print("Middle: "); Serial.print(middle, 3); Serial.print(" m | ");
  Serial.print("Expected: "); Serial.print(expected, 3); Serial.print(" m | ");
  Serial.print("Method: "); Serial.println(method);
}

void logDataToFile(float d0, float d1, float middle, float expected, const String& method) {
  logFile = SD.open(filename, FILE_WRITE);
  if (logFile) {
    unsigned long timestamp = millis();
    logFile.print(timestamp / 1000.0, 2); logFile.print(",");
    logFile.print(d0, 3); logFile.print(",");
    logFile.print(d1, 3); logFile.print(",");
    logFile.print(middle, 3); logFile.print(",");
    logFile.print(expected, 3); logFile.print(",");
    logFile.println(method);
    logFile.close();
  } else {
    Serial.println("Failed to write to SD card!");
  }
}

void logDataAuto(float d0, float d1, float middle, float expected, const String& method) {
  if (sdLoggingAvailable) {
    logDataToFile(d0, d1, middle, expected, method);
  } else {
    logDataToSerial(d0, d1, middle, expected, method);
  }
}