const int START_PIN = 2;
const int NUM_PIN = 17;
const int NUM_SAMP = 3;
const int SKIP_PIN = 14;
const int DELAY_TIME = 67;

int recentVals[NUM_PIN][NUM_SAMP];
int curStates[NUM_PIN];
int analogVal = -1;
int lastTime;

void setup() {
  Serial.begin(9600);
  Serial.print("#stDv\n");
  
  for (int i = 0; i < NUM_PIN; i++){
    curStates[i] = LOW;//default state up
    for (int j = 0; j < NUM_SAMP; j++){
      recentVals[i][j] = LOW;
    }
  }

  for (int i = START_PIN; i < NUM_PIN + 1; i++ ){
    //Serial.print("pin" + String(i) + " set");
    if (i == SKIP_PIN){
      continue; 
    }
    pinMode(i, INPUT);//init pin
  }
  
  lastTime=millis();
}

void loop() {
  int newAnalogVal = analogRead(A0);
  if ( abs(newAnalogVal - analogVal) > 20 ){
    analogVal = newAnalogVal;
    Serial.print("AgCh:" + String(analogVal) + "\n");
  }
  
  for (int i = 0; i < NUM_PIN; i++){
    int pinID;
    if( i + START_PIN < SKIP_PIN){
      pinID = i+2;
    } else {
      pinID = i + 3;
    }
    //Serial.print("scan:" + String(pinID) + "\n");
    
    int isLow = true;
    int isHigh = true;
    
    for (int j = 0; j < NUM_SAMP-1; j ++){
      if (recentVals[i][j] == HIGH){
        isLow = false;
      }else{
        isHigh = false;
      }
      recentVals[i][j] = recentVals[i][j+1];
    }
    
    recentVals[i][NUM_SAMP-1] = digitalRead(pinID);

    
    if (recentVals[i][NUM_SAMP-1] == HIGH){
      isLow = false;
    }else{
      isHigh = false;
    }
    
    if (isLow && curStates[i] == HIGH){
      curStates[i] = LOW;
      Serial.print("btUp:" + String(i) + "\n");
    }else if (isHigh && curStates[i] == LOW){
      curStates[i] = HIGH;
      Serial.print("btDn:" + String(i) + "\n");
    }
  }
  int newTime = millis();
  int passedTime = newTime - lastTime;
  if(passedTime < DELAY_TIME){
    delay(DELAY_TIME - passedTime);
  }
  lastTime = newTime;
  
}
