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
char *filename = "uwb-test-30cm.csv";

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
    logFile.println("Timestamp (s), Distance (m)");  // CSV Header
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

    Serial1.println(commands[i]);  // Send command
    delay(200);  // Wait for the command to process
  }
  Serial.println("Everything is setup!");
}

void loop() {
  static String receivedData = "";
  static unsigned long lastReadTime = 0;
  const unsigned long readInterval = 100; // Adjust for better timing

  if(millis() - lastReadTime > readInterval){
    lastReadTime = millis(); // Update last read timestamp
    while (Serial1.available()) {
      char c = Serial1.read();
      if (c == '\n') {  // End of a response line
        float distance = extractDistance(receivedData);

        if (!isnan(distance)) {
          Serial.println(distance, 2);
          logData(distance); 
        }

        receivedData = ""; // Clear buffer for next response
      } else {
        receivedData += c; // Append to buffer
      }
    }
  }

  // If no data has been received for a while, do not spam "Serial1 not available"
  if (millis() - lastReadTime > 2000) { // 2-second timeout
    Serial.println("Serial1 not available");
    lastReadTime = millis(); // Reset to avoid constant printing
  }
}

// Function to extract numeric value from string
float extractDistance(String input) {
  int startIndex = input.indexOf(':'); // Find position of ':'
  if (startIndex != -1) {
    String numPart = input.substring(startIndex + 1); // Get part after ':'
    numPart.trim(); // Remove any whitespace
    return numPart.toFloat(); // Convert to float
  }
  return NAN; // Return NaN if no number was found
}

// Function to log data to SD card
void logData(float distance) {
  logFile = SD.open(filename, FILE_WRITE);
  if (logFile) {
    unsigned long timestamp = millis(); // Get time in milliseconds
    logFile.print(timestamp / 1000.0, 2); // Convert to seconds
    logFile.print(",");
    logFile.println(distance, 2);
    logFile.close();
  } else {
    Serial.println("Failed to write to SD card!");
  }
}