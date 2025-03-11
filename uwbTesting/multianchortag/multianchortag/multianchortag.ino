#include <SPI.h>
//#include <SD.h>
#include "SdFat.h"
SdFat SD;

#define SD_CS_PIN SS

// Test with reduced SPI speed for breadboards.  SD_SCK_MHZ(4) will select
// the highest speed supported by the board that is not over 4 MHz.
// Change SPI_SPEED to SD_SCK_MHZ(50) for best performance.
#define SPI_SPEED SD_SCK_MHZ(4)

FsFile logFile;
char *filename = "multi-uwb-test-50cm.csv";

void setup() {
  Serial.begin(9600);

  Serial.print("Initializing SD card...");

  if (!SD.begin(SD_CS_PIN, SPI_SPEED)) {
    Serial.println("initialization failed!");
    return;
  }
  Serial.println("initialization done.");

  if (SD.exists(filename)) {
    Serial.println("Deleting existing file...");
    SD.remove(filename);
  }

  logFile = SD.open(filename, FILE_WRITE);
  if (logFile) {
    logFile.println("Timestamp (s), Anchor-0 (m), Anchor-1 (m), MiddlePoint (m)");  
    logFile.close();
  }

  Serial1.begin(115200);
  delay(500);

  const char *commands[] = {
    "AT+RST",               // Reset module
    "AT+anchor_tag=0,0",    // Set as "tag" with ID 0
    "AT+interval=5",        // Set sending interval (5-50)
    "AT+switchdis=1"        // Start localization
  };

  int numCommands = sizeof(commands) / sizeof(commands[0]);

  for (int i = 0; i < numCommands; i++) {
    Serial.print("Sending: ");
    Serial.println(commands[i]);

    Serial1.println(commands[i]);  
    delay(200);  // Wait for the command to process
  }
  Serial.println("Everything is setup!");
}

void loop() {
  static String receivedData = "";
  static unsigned long lastReadTime = 0;
  const unsigned long readInterval = 100; 

  static float distances[2] = { NAN, NAN }; // Stores distances for an0 and an1

  if (millis() - lastReadTime > readInterval) {
    lastReadTime = millis();
    while (Serial1.available()) {
      char c = Serial1.read();
      if (c == '\n') {  // End of a response line
        float distance = extractDistance(receivedData);
        int deviceId = extractAnchorDevice(receivedData);

        if (!isnan(distance) && deviceId >= 0 && deviceId < 2) {
          distances[deviceId] = distance;

          Serial.print("Anchor ");
          Serial.print(deviceId);
          Serial.print(": ");
          Serial.print(distance, 3);
          Serial.println(" m"); // Print distance in meters

          if (!isnan(distances[0]) && !isnan(distances[1])) {
            float dm = distanceToMiddle(distances[0], distances[1]);
            Serial.print("Distance to middle: ");
            Serial.print(dm, 3);
            Serial.println(" m"); // Print middle distance in meters
            
            // Log all three values (Anchor-0, Anchor-1, MiddlePoint)
            logData(distances[0], distances[1], dm);
          }
        }

        receivedData = ""; 
      } else {
        receivedData += c; 
      }
    }
  }

  // If no data has been received for a while, do not spam "Serial1 not available"
  if (millis() - lastReadTime > 2000) { 
    Serial.println("Serial1 not available");
    lastReadTime = millis(); // Reset to avoid constant printing
  }
}

int extractAnchorDevice(String input) {
  if (input.startsWith("an")) {
    int colonIndex = input.indexOf(':');
    if (colonIndex != -1) {
      String deviceIdStr = input.substring(2, colonIndex); // Extract the part after "an" and before ":"
      return deviceIdStr.toInt(); // Convert to integer
    }
  }
  return -1; // Return -1 if unknown format
}

// Function to extract numeric value from string format "an0: 0.03 m"
float extractDistance(String input) {
  Serial.println(input);
  int startIndex = input.indexOf(':'); 
  if (startIndex != -1) {
    String numPart = input.substring(startIndex + 1); 
    numPart.trim();
    return numPart.toFloat(); // Convert to float
  }
  return NAN; 
}

float distanceToMiddle(float d0, float d1) {
  const float anchorDistance = 0.184; // Distance between anchors in meters
  float middleX = anchorDistance / 2.0; // Middle point at 0.092 meters

  // Compute the perpendicular distance to the middle point using trilateration
  float x = (d0 * d0 - d1 * d1 + anchorDistance * anchorDistance) / (2.0 * anchorDistance);
  float d_m = sqrt(abs(d0 * d0 - x * x)); // Ensuring no negative sqrt

  return d_m; // Return distance to middle in meters
}

// Function to log data to SD card
// Function to log data to SD card
void logData(float d0, float d1, float middle) {
  logFile = SD.open(filename, FILE_WRITE);
  if (logFile) {
    unsigned long timestamp = millis(); // Get time in milliseconds
    logFile.print(timestamp / 1000.0, 2); // Convert to seconds
    logFile.print(",");
    logFile.print(d0, 3); // Anchor-0 distance in meters
    logFile.print(",");
    logFile.print(d1, 3); // Anchor-1 distance in meters
    logFile.print(",");
    logFile.println(middle, 3); // Distance to middle in meters
    logFile.close();
  } else {
    Serial.println("Failed to write to SD card!");
  }
}