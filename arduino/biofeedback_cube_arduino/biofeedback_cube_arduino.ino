#include <Wire.h>

const int ledPin = 13; // onboard LED
const short DELAY = 15;
int pulseSensorPin = 0;
int pulseVal = 0;
byte i2cAddress = 0x09;

void setup() {
  Wire.begin(i2cAddress);
//  Wire.onReceive(receiveEvent);
  Wire.onRequest(requestEvent);
  
  pinMode(ledPin, OUTPUT);
}
 
void loop() {
  pulseVal = analogRead(pulseSensorPin);
  analogWrite(ledPin, 255*((pulseVal-300) / 400));
  delay(DELAY);
}

//void receiveEvent(int howMany) {
//    char b1 = Wire.read(); // receive byte as a character
//    char b2 = Wire.read(); // receive byte as a character
//}

void requestEvent(int howMany) {
  Wire.write((byte *) &pulseVal, sizeof(int));
//  Serial.println('¯\_(ツ)_/¯');
}
