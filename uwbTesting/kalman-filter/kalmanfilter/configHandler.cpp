#include "configHandler.h"

void setUpConfig() {
  pinMode(yellowLED, OUTPUT);
  pinMode(greenLED, OUTPUT);

  pinMode(startButton, INPUT);

  //blink leds
  for (int i = 0; i < 4; i++) {
    digitalWrite(yellowLED, HIGH);
    digitalWrite(greenLED, HIGH);
    delay(100);

    digitalWrite(yellowLED, LOW);
    digitalWrite(greenLED, LOW);
    delay(100);
  }
}

bool listenForStarted() {
  static bool lastState = LOW;
  bool currentState = digitalRead(startButton);
  if (currentState == HIGH && lastState == LOW) {
    Serial.println("started");
    lastState = currentState;
    return true;  // rising edge
  }
  lastState = currentState;
  return false;
}

bool getStarted() {
  return digitalRead(startButton) == HIGH;
}

void updateModeLEDs(Mode mode, bool started) {
  static unsigned long lastBlink = 0;
  static bool ledState = false;
  const unsigned long blinkInterval = 300;

  int activeLED = -1, inactiveLED = -1;

  switch (mode) {
    case WARMUP:
      digitalWrite(greenLED, HIGH);
      digitalWrite(yellowLED, HIGH);
      return;  // Show both LEDs solidly ON during warmup

    case CALIBRATIONMODE:
      activeLED = yellowLED;
      inactiveLED = greenLED;
      break;

    case TESTMODE:
      activeLED = greenLED;
      inactiveLED = yellowLED;
      break;

    case UNKNOWN:
      // Blink alternately
      if (millis() - lastBlink >= blinkInterval) {
        ledState = !ledState;
        digitalWrite(greenLED, ledState);
        digitalWrite(yellowLED, !ledState);
        lastBlink = millis();
      }
      return;
  }

  // For CALIBRATIONMODE and TESTMODE:
  digitalWrite(inactiveLED, LOW);
  if (started) {
    if (millis() - lastBlink >= blinkInterval) {
      ledState = !ledState;
      digitalWrite(activeLED, ledState ? HIGH : LOW);
      lastBlink = millis();
    }
  } else {
    digitalWrite(activeLED, HIGH);
  }
}