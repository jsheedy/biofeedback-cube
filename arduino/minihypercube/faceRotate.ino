  void faceRotate() {
    count++;
    CRGB color = CHSV(count * 42,255,255);
    fadeOut(0);
    FastLED.clear();
    faceColor(count % 6, color);
    fadeIn(0);
    FastLED.delay(1);
  }
