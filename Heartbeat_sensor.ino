// Constants
const float rThreshold = 0.7;
const float decayRate = 0.01;
const float thrRate = 0.05;
const int minDiff = 5;

// Current values
float maxValue = 0;
float minValue = 1024;
float threshold = 512;

// Timestamp of the last heartbeat
long lastHeartbeat = 0;

// Last value to detect crossing the threshold
int lastValue = 1024;

void setup() {
  Serial.begin(9600);
}
  
void loop() {
  int currentValue = analogRead(A0);
  maxValue = max(maxValue, currentValue);
  minValue = min(minValue, currentValue);

  // Detect Heartbeat
  float nthreshold = (maxValue - minValue) * rThreshold + minValue;
  threshold = threshold * (1-thrRate) + nthreshold * thrRate;
  threshold = min(maxValue, max(minValue, threshold));
  
  if(currentValue >= threshold 
      && lastValue < threshold 
      && (maxValue-minValue) > minDiff 
      && millis() - lastHeartbeat > 300) {
        
    if(lastHeartbeat != 0) {
      // Show Results
      int bpm = 60000/(millis() - lastHeartbeat);
      if(bpm > 50 && bpm < 250) {
        Serial.print("Heart Rate (bpm): ");
        Serial.println(bpm);
      }
    }
    lastHeartbeat = millis();
  }

  // Decay for max/min
  maxValue -= (maxValue-currentValue)*decayRate;
  minValue += (currentValue-minValue)*decayRate;

  lastValue = currentValue;
  delay(20);
}
