#include <IRremote.h>

const int RECV_PIN = 11;
IRrecv irrecv(RECV_PIN);
decode_results results;

void setup(){
  Serial.begin(9600);
  irrecv.enableIRIn();
  irrecv.blink13(true);
}

unsigned int buttonValues[] = {
  0xA25D,
  0x629D,
  0xE21D,
  0x22DD,
  0x02FD,
  0xC23D,
  0xE01F,
  0xA857,
  0x906F,
  0x6897,
  0x9867,
  0xB04F,
  0x30CF,
  0x18E7,
  0x7A85,
  0x10EF,
  0x38C7,
  0x5AA5,
  0x42BD,
  0x4AB5,
  0x52AD
};

unsigned long lastPressTime = 0;

boolean beenPressing = false;

void loop(){
  //Serial.println("loop");
  if (irrecv.decode(&results)){
      lastPressTime = millis();
      if (results.value != 0xFFFFFFFF){
          for (int i = 0; i < 21; i++){
              if ( abs(  (int) (results.value & 0xFFFF) - buttonValues[i] ) < 256 ){
                  Serial.println(i);
                  beenPressing = true;
                  break;
              }
          }
      }
      irrecv.resume();
  }else{
    if (beenPressing and (millis() - lastPressTime) > 125 ){
      beenPressing = false;
      Serial.println('x');
    }
  }
}
