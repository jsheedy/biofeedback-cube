
void spotlight() {
  FastLED.clear();
  int phase = 255/4;
  int value = dim8_video(sin8(millis()/10));
  CHSV color = CHSV(200, 255, value);
  faceColor(SIDE_3, color);

  value = dim8_video(sin8(millis()/10+phase));
  color = CHSV(200, 255, value);
  faceColor(SIDE_0, color);
  
  value = dim8_video(sin8(millis()/10+2*phase));
  color = CHSV(200, 255, value);
  faceColor(SIDE_1, color);
    
  value = dim8_video(sin8(millis()/10+3*phase));
  color = CHSV(200, 255, value);
  faceColor(SIDE_2, color);
}
