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

void fadeIn(int delay, int inc) {
  for (int i=0; i<256; i+=inc) {
    FastLED.setBrightness(dim8_raw(i));
    FastLED.delay(delay);
  }
}
void fadeIn(int delay) {
  fadeIn(delay, 1);
}

void fadeOut(int delay, int inc) {
  for (int i=255; i>0; i-=inc) {
    FastLED.setBrightness(dim8_raw(i));
    FastLED.delay(delay);
  } 
}
void fadeOut(int delay) {
  fadeOut(delay, 1);
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

void rainbow() {
  faceColor(SIDE_0, CHSV(random(0,256), 255, 255));
  faceColor(SIDE_1, CHSV(random(0,256), 255, 255));
  faceColor(SIDE_2, CHSV(random(0,256), 255, 255));
  faceColor(SIDE_3, CHSV(random(0,256), 255, 255));
  faceColor(SIDE_4, CHSV(random(0,256), 255, 255));
  faceColor(SIDE_5, CHSV(random(0,256), 255, 255)); 
}

void faceChase() {
  for (int i=0; i < 256; i+=7) {
    FastLED.clear();
    faceColor(i%3, CHSV(i, 255, 255));
    FastLED.delay(150);
  }
}

void heartBeat() {
  
//  CRGB color = CRGB(245,20,20);
  CRGB color = CHSV(0, 255, 255);

//  FastLED.setBrightness(0);
  fill_solid( &(leds[0]), NUM_LEDS, color);
//  fadeIn(0,2);
//  fadeOut(1,2);
//  
//  color = CRGB(255,0,255);
//  fill_solid( &(leds[0]), NUM_LEDS, color);
//  fadeIn(0,2);
//  fadeOut(3);
  
//glitch
  fadeIn(0,2);
  fadeOut(0,2);
  fill_solid( &(leds[0]), NUM_LEDS, color);

  fadeIn(0,2);
  for (int i=255; i>0; i--) {
    if (i > 40) {
      color = CHSV(0, i, 255);
      fill_solid( &(leds[0]), NUM_LEDS, color);
      FastLED.setBrightness(i);
  //        FastLED.setBrightness(dim8_raw(i));
  //
      FastLED.delay(5);  
    } else {
      FastLED.setBrightness(i);
      FastLED.delay(20);
    }
    
  }
  //glitch
//  for (int i=0; i<200; i++ ){
//
//    for (int j=0; j<NUM_LEDS; j++ ){
//      leds[j] = CHSV(sin8(j*10+i), 255,i);
//    }
//    FastLED.delay(4);
//  }

}

void heartBeats(int count) {
  for (int i=0; i<count; i++) {
    heartBeat();
  }
}

void dawn() {
  fadeOut(5);
  fill_solid( &(leds[0]), NUM_LEDS, CRGB(255,255,255));
  fadeIn(20);
  fadeOut(10);
}

void loop() {
  heartBeats(1);
  FastLED.setBrightness(255);

//  switch(random(0,7)) {
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
//    case 4:
//      dawn();
//      break;
//    case 5:
//      rainbow();
//      break;
//    case 6:
//      faceChase();
//      break;
//  }

//  FastLED.delay(random(0,200));
}
