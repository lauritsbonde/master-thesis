#include "LED.h"

int leds[] = {11,12,13};

const int LED_COUNT = sizeof(leds) / sizeof(leds[0]);

void coolLightshow(int durationMillis = 5000) {
  unsigned long startTime = millis();
  int delayTime = 100;

  while (millis() - startTime < durationMillis) {
    // Forward sweep
    for (int i = 0; i < LED_COUNT; i++) {
      for (int j = 0; j < LED_COUNT; j++) {
        digitalWrite(leds[j], j == i ? HIGH : LOW);
      }
      delay(delayTime);
    }

    // Reverse sweep with pulse
    for (int i = LED_COUNT - 1; i >= 0; i--) {
      for (int j = 0; j < LED_COUNT; j++) {
        digitalWrite(leds[j], j == i ? HIGH : LOW);
      }
      delay(delayTime);
    }

    // Pulse all together once
    for (int pulse = 0; pulse < 2; pulse++) {
      for (int j = 0; j < LED_COUNT; j++) {
        digitalWrite(leds[j], HIGH);
      }
      delay(100);
      for (int j = 0; j < LED_COUNT; j++) {
        digitalWrite(leds[j], LOW);
      }
      delay(100);
    }
  }

  // Turn off all LEDs at end
  for (int i = 0; i < LED_COUNT; i++) {
    digitalWrite(leds[i], LOW);
  }
}

void setupLEDS(){
  for(int i = 0; i < LED_COUNT; i++){
    pinMode(leds[i], OUTPUT);
  }

  coolLightshow(2500);
}

void espReady(){
  digitalWrite(leds[0], HIGH);
}

void espNotReady(){
  digitalWrite(leds[0], LOW);
}

void motorRuns(){
  digitalWrite(leds[1], HIGH);
  digitalWrite(leds[2], LOW);
}

void motorStop(){
  digitalWrite(leds[1], LOW);
  digitalWrite(leds[2], HIGH);
}


