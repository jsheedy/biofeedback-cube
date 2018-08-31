
void glitchDiscoCube() {

     int sides[] = {SIDE_0, SIDE_1, SIDE_2, SIDE_3, SIDE_4, SIDE_5};

     for (int i=0; i<6; i++) {
       CRGB color = CHSV(random(0,256),255,255);
       faceColor(sides[i], color);
       FastLED.delay(random(0,400));  
       FastLED.clear();      
     }
}

