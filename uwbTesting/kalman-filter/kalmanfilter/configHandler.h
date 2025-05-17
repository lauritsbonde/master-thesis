#ifndef CONFIG_HANDLER_H
#define CONFIG_HANDLER_H

#include <Arduino.h>

// Pin definitions
#define yellowLED 5    // on if calibration mode
#define greenLED 6     // in if test mode
#define startButton 9  // start test or calibration when the button is pressed


// Mode enum
enum Mode { WARMUP,
            CALIBRATIONMODE,
            TESTMODE,
            UNKNOWN };

// Function declarations
void setUpConfig();

bool getStarted();
bool listenForStarted();

void updateModeLEDs(Mode mode, bool started);

#endif