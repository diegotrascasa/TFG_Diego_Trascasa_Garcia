const int ledPin = 13;  // Pin del LED
const int calibrationTime = 5000;  // Tiempo para calibrar el umbral (en milisegundos)
const int ledOnTime = 200;  // Tiempo en milisegundos para mantener el LED encendido
int threshold = 0;  // Umbral para detección de latido
int signalMax = 0;  // Valor máximo de la señal
int signalMin = 1023;  // Valor mínimo de la señal
unsigned long calibrationStartTime;
unsigned long lastBeatTime = 0;  // Tiempo del último latido detectado

void setup() {
  // Initialize the serial communication
  Serial.begin(9600);

  // Setup for leads off detection LO+
  pinMode(10, INPUT);
  // Setup for leads off detection LO-
  pinMode(11, INPUT);

  // Pin for LED
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);

  // Start calibration
  calibrationStartTime = millis();
}

void loop() {
  // Check if leads are off
  if (digitalRead(10) == 1 || digitalRead(11) == 1) {
    Serial.println(0);
  } else {
    int signal = analogRead(A1);
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
      // Detect heartbeat and control LED
      if (signal > threshold) {
        lastBeatTime = millis();
        digitalWrite(ledPin, HIGH);
      }

      // Turn off the LED after the defined time has passed
      if (millis() - lastBeatTime > ledOnTime) {
        digitalWrite(ledPin, LOW);
      }
    }
  }

  // Wait for a bit to keep serial data from saturating
  delay(10);
}



// Explicación de las modificaciones:
//Definición del LED: Se añade una constante ledPin para definir el pin del LED y se configura en el setup().
//Calibración:
//Durante los primeros 5000 milisegundos (5 segundos), el programa lee los valores máximos y mínimos de la señal para establecer un umbral inicial.
//signalMax y signalMin se usan para almacenar los valores máximos y mínimos de la señal durante el periodo de calibración.
//threshold se calcula como el promedio de signalMax y signalMin.
//Detección de Latidos:
//Después del periodo de calibración, si la señal excede el umbral, el LED se enciende; de lo contrario, se apaga.
//Salida Serial: Solo se envía el valor de A1 al monitor serial, independientemente del estado de los electrodos.