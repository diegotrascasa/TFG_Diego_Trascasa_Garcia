const int ledPin = 13;  // Pin del LED
const int calibrationTime = 5000;  // Tiempo para calibrar el umbral (en milisegundos)
const int tiempo_led = 200;  // Tiempo en milisegundos para mantener el LED encendido
int threshold = 0;  // Umbral para detección de latido
int signalMax = 0;  // Valor máximo de la señal
int signalMin = 1023;  // Valor mínimo de la señal
unsigned long calibrationStartTime; // Variable
unsigned long ultimo_latido = 0;  // Tiempo del último latido detectado

void setup() {
  Serial.begin(9600);

  // LO+
  pinMode(10, INPUT);
  // LO-
  pinMode(11, INPUT);
  // LED 13
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);

  // Inicia calibracion
  calibrationStartTime = millis();
}

void loop() {
  if (digitalRead(10) == 1 || digitalRead(11) == 1) {
    Serial.println(0);
  } else {
    int signal = analogRead(A1);
    Serial.println(signal);

    // Calibra threshold
    if (millis() - calibrationStartTime < calibrationTime) {
      if (signal > signalMax) {
        signalMax = signal;
      }
      if (signal < signalMin) {
        signalMin = signal;
      }
      threshold = (signalMax + signalMin) / 2;
    } else {
      // Detecta latido and enciende LED
      if (signal > threshold) {
        ultimo_latido = millis();
        digitalWrite(ledPin, HIGH);
      }

      // Apaga el LED cuando pasen los 200ms
      if (millis() - ultimo_latido > tiempo_led) {
        digitalWrite(ledPin, LOW);
      }
    }
  }
  delay(10);
}
