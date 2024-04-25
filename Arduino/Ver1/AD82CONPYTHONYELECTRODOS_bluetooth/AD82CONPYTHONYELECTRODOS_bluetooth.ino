#include <SoftwareSerial.h>

SoftwareSerial bluetooth(0, 1); // RX, TX

void setup() {
  // Inicializar la comunicación serial con el módulo Bluetooth:
  bluetooth.begin(38400);
  Serial.begin(9600);
  pinMode(10, INPUT); // Setup for leads off detection LO +
  pinMode(11, INPUT); // Setup for leads off detection LO -

}

void loop() {
  
  if((digitalRead(10) == 1)||(digitalRead(11) == 1)){
    Serial.println('0');
    bluetooth.println('0');
    
  }
  else{
    // send the value of analog input 0:
      Serial.println(analogRead(A1));
      bluetooth.println(analogRead(A1));

  }
  //Wait for a bit to keep serial data from saturating
  delay(10);
}
