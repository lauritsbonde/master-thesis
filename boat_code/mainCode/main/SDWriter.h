// SDWriter.h
#pragma once

#include <Arduino.h>

void SDWriterSetup();
void SDWrite(const String& text);
void startLogging();
void stopLogging();
void loggingLoop();

extern bool SD_shall_log;
extern int counter;