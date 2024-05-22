const int ledPin = 13;  // Pin del LED
const int calibrationTime = 5000;  // Tiempo para calibrar el umbral (en milisegundos)
const int ledOnTime = 200;  // Tiempo en milisegundos para mantener el LED encendido
int threshold = 0;  // Umbral para detección de latido
int signalMax = 0;  // Valor máximo de la señal
int signalMin = 1023;  // Valor mínimo de la señal
unsigned long calibrationStartTime;
unsigned long lastBeatTime = 0;  // Tiempo del último latido detectado

void setup() {
  Serial.begin(9600);
  pinMode(10, INPUT);
  pinMode(11, INPUT);

  // Pin LED
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);

  // Calibracion de 5 segundos
  calibrationStartTime = millis();
}

void loop() {
  if (digitalRead(10) == 1 || digitalRead(11) == 1) {
    Serial.println(0);
  } else {
    int signal = analogRead(A1);
    Serial.println(signal);

    // Calibra el threshold
    if (millis() - calibrationStartTime < calibrationTime) {
      if (signal > signalMax) {
        signalMax = signal;
      }
      if (signal < signalMin) {
        signalMin = signal;
      }
      threshold = (signalMax + signalMin) / 2;
    } else {
      // Detecta el latido y enciende LED
      if (signal > threshold) {
        lastBeatTime = millis();
        digitalWrite(ledPin, HIGH);
      }

      // Apagar el led tras los 200 ms
      if (millis() - lastBeatTime > ledOnTime) {
        digitalWrite(ledPin, LOW);
      }
    }
  }
  delay(10);
}

