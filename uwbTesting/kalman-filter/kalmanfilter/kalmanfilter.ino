#include <SPI.h>
#include "SdFat.h"
#include "configHandler.h"
#include "SimpleKalmanFilter.h"

// sd card settings
SdFat SD;
#define SD_CS_PIN SS
#define SPI_SPEED SD_SCK_MHZ(4)

float distance = 1.00;  // triangle height in m
FsFile logFile;
char filename[64];
bool sdLoggingAvailable = false;

float baseLength = 0.184;  // In meters (distance between anchors)

float expected = 0;  // calculated distance to the anchors, based on distance (triangle height)

Mode mode = UNKNOWN;
bool started = false;

const int warmupSamples = 20;
int warmupCount = 0;

const int calibrationSamples = 30;
int calibrationCount = 0;

float sumAnchor0 = 0;
float sumAnchor1 = 0;

float calibrationOffset0 = 0;  // for anchor 0
float calibrationOffset1 = 0;  // for anchor 1

SimpleKalmanFilter kalman0(0.05, 0.05, 0.01);
SimpleKalmanFilter kalman1(0.05, 0.05, 0.01);

void setup() {
  Serial.begin(9600);

  Serial1.begin(115200);
  delay(500);

  Serial.println("Serial1 setup");

  const char* commands[] = {
    "AT+RST",
    "AT+anchor_tag=0,0",
    "AT+interval=5",
    "AT+switchdis=1"
  };

  for (const char* cmd : commands) {
    Serial1.println(cmd);
    delay(200);
  }

  setUpConfig();

  setupLogging(distance, filename);
  delay(500);
  Serial.println("Logging setup");

  Serial.println("Everything is setup!");

  expected = distanceFromTopToAnchor(baseLength, distance);
  Serial.print("Expected anchor distance: ");
  Serial.println(expected, 3);
}

void loop() {
  // Detect button press to "start"
  if (!started && listenForStarted()) {
    started = true;
    mode = WARMUP;
    Serial.println("Started!");
  };

  // Update LED state based on current mode and started flag
  updateModeLEDs(mode, started);

  if (!started) {
    static bool printed = false;
    if (!printed) {
      Serial.println("Press green button to start experiment!");
      printed = true;
    }
    return;
  }

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

        if (deviceId == 0 || deviceId == 1) {
          distances[deviceId] = distanceVal;
        }

        if (!isnan(distances[0]) && !isnan(distances[1])) {
          float raw0 = distances[0] + calibrationOffset0;
          float raw1 = distances[1] + calibrationOffset1;

          float d0 = raw0;
          float d1 = raw1;
          float dm = NAN;
          String method = "none";

          if (mode == WARMUP) {
            warmupCount++;
            if (warmupCount >= warmupSamples) {
              mode = CALIBRATIONMODE;
            }

          } else if (mode == CALIBRATIONMODE && calibrationCount < calibrationSamples) {
            sumAnchor0 += distances[0];
            sumAnchor1 += distances[1];
            calibrationCount++;

            if (calibrationCount >= calibrationSamples) {
              float avg0 = sumAnchor0 / calibrationSamples;
              float avg1 = sumAnchor1 / calibrationSamples;

              calibrationOffset0 = expected - avg0;
              calibrationOffset1 = expected - avg1;

              distances[0] = NAN;
              distances[1] = NAN;

              kalman0.setEstimate(calibrationOffset0 + avg0);
              kalman1.setEstimate(calibrationOffset1 + avg1);

              mode = TESTMODE;
            }

          } else if (mode == TESTMODE) {
            // Only apply Kalman filter and trilateration during TESTMODE
            if (!isnan(raw0) && !isnan(raw1)) {
              d0 = kalman0.updateEstimate(raw0);
              d1 = kalman1.updateEstimate(raw1);

              bool violatesTriangle = (d0 + d1 <= baseLength || fabs(d0 - d1) >= baseLength);

              if (violatesTriangle) {
                method = "estimate";
                dm = trilaterationEstimate(d0, d1, baseLength);
                if (dm == 0.0f) {
                  method = "fallback";
                  dm = trilaterationFallback(d0, d1);
                }
              } else {
                dm = trilaterationHeight(d0, d1, baseLength);
                if (dm < 0.0f) {
                  method = "estimate";
                  dm = trilaterationEstimate(d0, d1, baseLength);
                  if (dm == 0.0f) {
                    method = "fallback";
                    dm = trilaterationFallback(d0, d1);
                  }
                } else {
                  method = "direct";
                }
              }
            } else {
              Serial.println("[WARN] Skipping filter/trilateration — raw NaN in TESTMODE");
            }
          }

          // Always log the values — even if in warmup/calibration
          logDataAuto(raw0, raw1, d0, d1, dm, expected, method, mode);
        } else {
          Serial.print("invalid distances: ");
          Serial.print("d0: ");
          Serial.print(distances[0]);
          Serial.print(" - d1: ");
          Serial.println(distances[1]);
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
