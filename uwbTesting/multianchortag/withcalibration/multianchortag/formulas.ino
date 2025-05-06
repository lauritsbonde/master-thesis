float distanceFromTopToAnchor(float baseMeters, float heightMeters) {
  float halfBase = baseMeters / 2.0;
  return sqrt(halfBase * halfBase + heightMeters * heightMeters);
}

float trilaterationHeight(float d0, float d1, float base) {
  float x = (d0 * d0 - d1 * d1) / (2.0f * base);
  if (fabs(x) > base / 2.0f) {
    // Serial.println("x is outside base: invalid triangle geometry");
    return -1.0f;
  }
  float ySquared = d0 * d0 - x * x;

  if (ySquared < 0.0f) {
    // Serial.println("Invalid geometry: negative y²");
    return -1.0f;
  }
  return sqrt(ySquared);
}

float trilaterationEstimate(float d0, float d1, float base) {
  float a = min(d0, d1);
  float b = max(d0, d1);
  float x = (a * a - b * b) / (2.0f * base);
  float ySquared = a * a - x * x;

  if (ySquared < 0.0f) {
    // Serial.println("Even fallback estimate failed: negative y²");
    ySquared = 0.0f;
  }
  return sqrt(ySquared);
}

float trilaterationFallback(float d0, float d1) {
  float minD = min(d0, d1);
  // Serial.println("Using fallback vertical estimate based on min(d0, d1): ");
  return minD;
}
