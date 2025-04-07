#include "LED.h"

int leds[] = {5,6,7};

const int LED_COUNT = sizeof(leds) / sizeof(leds[0]);


void setupLEDS(){
  for(int i = 0; i < LED_COUNT; i++){
    pinMode(leds[i], OUTPUT);
  }

  for(int i = 0; i < 3; i++){
    for(int j = 0; j < LED_COUNT; j++){
      digitalWrite(leds[j], HIGH);
    }
    delay(200);
    for(int j = 0; j < LED_COUNT; j++){
      digitalWrite(leds[j], LOW);
    }
    delay(200);
  }
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

