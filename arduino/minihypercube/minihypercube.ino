#include <FastLED.h>

#define NUM_LEDS 6

// FIXME: how to address the SPI pins on itsy bitsy board
#define DATA_PIN    A1//16
#define CLOCK_PIN   A0 //15
#define KNOB_1_PIN  A4

CRGB leds[NUM_LEDS];

void setup() {
  // APA102 is dotstars https://github.com/FastLED/FastLED/wiki/Chipset-reference
  FastLED.addLeds<APA102, DATA_PIN, CLOCK_PIN, BGR>(leds, NUM_LEDS);
  FastLED.setBrightness(0xff);

  // FastLED.addLeds<APA102, BGR>(leds, NUM_LEDS);
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
  Serial.begin(9600); // open the serial port at 9600 bps:

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
  FastLED.clear();
  FastLED.setBrightness(0);
  CRGB baseline = CRGB(0,0,20);
  CRGB color = baseline + CHSV(10, 255, 255);
  fill_solid( &(leds[0]), NUM_LEDS, color);

  fadeIn(0,2);
  fadeOut(0,2);
  color = baseline + CHSV(0, 255, 255);
  fill_solid( &(leds[0]), NUM_LEDS, color);
  fadeIn(0,2);

  unsigned long t0 = millis();
  unsigned long t1 = 0;
  unsigned long dt = 1500;
  unsigned long end = t0 + dt;

  while(t1 < dt) {
    fract8 fract = t1 * 256 / dt;
    byte s = lerp8by8(255,0,fract);
    color = baseline + CHSV(fract / 2, s, 255);
    FastLED.setBrightness(s);
    fill_solid( &(leds[0]), NUM_LEDS, color);
    FastLED.show();
    t1 = millis() - t0;
  }
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

// from https://www.reddit.com/r/FastLED/comments/b2mlvf/gamma_correction/
void adjustGamma()
{
  for (uint16_t i = 0; i < NUM_LEDS; i++)
  {
    leds[i].r = dim8_video(leds[i].r);
    leds[i].g = dim8_video(leds[i].g);
    leds[i].b = dim8_video(leds[i].b);
  }
}

void wave() {
  long t = millis();
  FastLED.setBrightness(10);
  for(int i=0; i<NUM_LEDS; i++ ) {
    leds[i] = CRGB(0,0,sin8(t/4+i*15));
  }
  FastLED.show();
}

void waves() {
  for(int i=0; i<2000; i++ ) {
    wave();
  }
}

void loop() {
//  heartBeats(1);
  // FastLED.delay(random8());
//  waves();
  int val = analogRead(KNOB_1_PIN) / 4;
  Serial.print(val);
  Serial.print("\n");
  leds[0] = CRGB(val, 0, 0);
  leds[1] = CRGB(0, val, 0);
  leds[2] = CRGB(0, 0, val);

//  for(int i=0; i<NUM_LEDS; i++ ) {
//    leds[i] = CRGB(0, val, 0);
//    leds[i] = CHSV(val, 255, 200);
//
//  }
  adjustGamma();
  FastLED.show();

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

  FastLED.delay(5);
}
