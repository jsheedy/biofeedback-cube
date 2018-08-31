#include <FastLED.h>

#define NUM_LEDS 18

// FIXME: how to address the SPI pins on itsy bitsy board
#define DATA_PIN    A1//16
#define CLOCK_PIN   A0 //15

CRGB leds[NUM_LEDS];

void setup() {
  // APA102 is dotstars https://github.com/FastLED/FastLED/wiki/Chipset-reference
  FastLED.addLeds<APA102, DATA_PIN, CLOCK_PIN, BGR>(leds, NUM_LEDS);
  // FastLED.addLeds<APA102, BGR>(leds, NUM_LEDS);
  Serial.begin(9600);
  Serial.println('woot');
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
}

void faceColor(int face, const struct CRGB & color) {
  leds[3*face + 0] = color;
  leds[3*face + 1] = color;
  leds[3*face + 2] = color;
}

int count = 0;

void fadeIn(int delay) {
  for (int i=0; i<256; i++) {
    FastLED.setBrightness(dim8_raw(i));
    FastLED.delay(delay);
  }
}

void fadeOut(int delay) {
  for (int i=255; i>0; i--) {
    FastLED.setBrightness(dim8_raw(i));
    FastLED.delay(delay);
  } 
}

#define SIDE_0 0
#define SIDE_1 3
#define SIDE_2 2
#define SIDE_3 1
#define SIDE_4 4
#define SIDE_5 5

void bomb() {
  fill_solid( &(leds[0]), NUM_LEDS, CRGB(255, 255, 255));
  FastLED.delay(random(0,100));
}

void loop() {
//  switch(random(0,6)) {
//    case 0:
//      hueRotate();
//      break;
//    case 1:
//      faceRotate();
//      break;
//    case 2:
//      glitchDiscoCube();
//      break;
//    case 3:
//      spotlight();
//      break;
//  }

//  if (millis() % 200 ==0) {
//    bomb();
//  }

  fill_solid( &(leds[0]), NUM_LEDS, CRGB(255,255,255));
  fadeIn(20);
  fadeOut(20);
  FastLED.setBrightness(255);
  faceColor(SIDE_0, CHSV(random(0,256), 255, 255));
  faceColor(SIDE_1, CHSV(random(0,256), 255, 255));
  faceColor(SIDE_2, CHSV(random(0,256), 255, 255));
  faceColor(SIDE_3, CHSV(random(0,256), 255, 255));
  faceColor(SIDE_4, CHSV(random(0,256), 255, 255));
  faceColor(SIDE_5, CHSV(random(0,256), 255, 255));
  FastLED.delay(300);
}
