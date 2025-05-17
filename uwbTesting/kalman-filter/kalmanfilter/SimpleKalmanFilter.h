#ifndef SIMPLE_KALMAN_FILTER_H
#define SIMPLE_KALMAN_FILTER_H

class SimpleKalmanFilter {
  float estimate;
  float errorEstimate;
  float errorMeasure;
  float q;

public:
  SimpleKalmanFilter(float mea_e, float est_e, float q);
  float updateEstimate(float measurement);
  void setEstimate(float est);
};

#endif