

struct record
{
  int speed;
  int count;
};

typedef struct record HueRotate;

HueRotate _hrg = {1, 0};


void hueRotate() {
  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i] = CHSV(i+_hrg.count, 255,255);
  }
  FastLED.show();
  _hrg.count += _hrg.speed;
}
