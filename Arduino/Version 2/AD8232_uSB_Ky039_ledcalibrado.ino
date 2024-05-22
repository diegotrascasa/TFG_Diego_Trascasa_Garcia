const int ledPin = 13;  // Pin del LED
const int sensorPin = A0;  // Pin del sensor KY-039
const int calibrationTime = 5000;  // Tiempo para calibrar el umbral (en milisegundos)
int threshold = 0;  // Umbral para detección de latido
int signalMax = 0;  // Valor máximo de la señal
int signalMin = 1023;  // Valor mínimo de la señal
unsigned long calibrationStartTime;
bool isCalibrating = true;

void setup() {
  // Initialize the serial communication
  Serial.begin(9600);

  // Pin for LED
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);

  // Start calibration
  calibrationStartTime = millis();
}

void loop() {
  int signal = analogRead(sensorPin);
  Serial.println(signal);

  // Calibrate threshold
  if (millis() - calibrationStartTime < calibrationTime) {
    if (signal > signalMax) {
      signalMax = signal;
    }
    if (signal < signalMin) {
      signalMin = signal;
    }
    threshold = (signalMax + signalMin) / 2;
  } else {
    if (isCalibrating) {
      // Finish calibration
      isCalibrating = false;
      Serial.print("Calibration complete. Threshold: ");
      Serial.println(threshold);
    }

    // Detect heartbeat and control LED
    if (signal > threshold) {
      digitalWrite(ledPin, HIGH);
    } else {
      digitalWrite(ledPin, LOW);
    }
  }

  // Wait for a bit to keep serial data from saturating
  delay(10);
}
