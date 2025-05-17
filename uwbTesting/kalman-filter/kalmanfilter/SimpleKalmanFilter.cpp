#include "SimpleKalmanFilter.h"
#include <math.h>
#include <Arduino.h>

SimpleKalmanFilter::SimpleKalmanFilter(float mea_e, float est_e, float q) {
  this->errorMeasure = mea_e;
  this->errorEstimate = est_e;
  this->q = q;
  this->estimate = 0;
}

float SimpleKalmanFilter::updateEstimate(float measurement) {
  float combinedError = errorEstimate + errorMeasure;
  float kalmanGain = errorEstimate / combinedError;
  estimate = estimate + kalmanGain * (measurement - estimate);
  errorEstimate = (1.0 - kalmanGain) * errorEstimate + fabs(estimate - measurement) * q;
  return estimate;
}

void SimpleKalmanFilter::setEstimate(float est) {
  estimate = est;
}