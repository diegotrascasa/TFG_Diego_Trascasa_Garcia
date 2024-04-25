#include <SoftwareSerial.h>

SoftwareSerial bluetooth(0, 1); // RX, TX

void setup() {
  // Inicializar la comunicación serial con el módulo Bluetooth:
  bluetooth.begin(38400);

  // Inicializar la comunicación serial para la depuración en el monitor serie:
  Serial.begin(9600);
}

void loop() {
  // Leer el valor del pin analógico A0:
  int sensorValue = analogRead(A0);

  // Enviar el valor leído a través del módulo Bluetooth:
  bluetooth.println(sensorValue);

  // Imprimir el valor leído en el monitor serie:
  Serial.println(sensorValue);

  // Esperar un breve periodo para evitar saturar la comunicación serie:
  delay(10);
}

