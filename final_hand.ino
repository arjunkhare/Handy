#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

float conv = 1.11;

//set up data stuff
char inData[10];
int index;
boolean started = false;
boolean ended = false;
boolean newLine = false;
int inpt[19];
int cln = 0;
boolean upd = false;

Adafruit_PWMServoDriver rightHand = Adafruit_PWMServoDriver();
Adafruit_PWMServoDriver leftHand = Adafruit_PWMServoDriver(0x41);

int sgnL[] = {1,1,1,1,1};
int sgnR[] = {1,1,1,1,1};

int positionInitalL[] = {300, 500, 430, 345, 240, 130, 100, 100, 150, 100}; //intial position

//do not exceed 430 on channel 2
//do not go far beyond on channel 3 and 4


int positionInitalR[] = {300, 500, 250, 320, 220, 400, 250, 250, 450, 450}; //inital position

//SET UP THE MAXIMUN AND MINIMUM VALUES
int minL[] = {150,150,175,225,190,130,100,100,150,100};
int maxL[] = {500,500,430,400,300,400,400,400,400,400};

int minR[] = {150,150,100,250,200,150,250,250,250,200};
int maxR[] = {500,500,395,400,300,400,550,450,450,450};

//initialize the position arrays
int posR[9];
int posL[9];

void setup() {
  // put your setup code here, to run once:
Serial.begin(9600);

//wait for the serial conections
while(!Serial){
  delay(1);
}

Serial.println("get ready for this jelly");

rightHand.begin();
leftHand.begin();

rightHand.setPWMFreq(50); //makes servo happy
leftHand.setPWMFreq(50); //makes servo happy

//set up the initial position..... start bammmmmm
for (int i = 0; i<10;i++){
  leftHand.setPWM(i,0,positionInitalL[i]);
  rightHand.setPWM(i,0,positionInitalR[i]);
}

//initialize the position array
for(int i = 0; i<10; i++){
  posR[i]=positionInitalR[i];
  posL[i]=positionInitalL[i];
}

}


void loop() {
while(Serial.available() > 0) { //check for data
  char aChar = Serial.read();
  if (aChar == '~'){
    newLine = true;
  }
  else if(aChar == '<'){
    started = true;
    index = 0;
    inData[index] = '\0';
  }
  else if (aChar == '>'){
    ended = true;
  }
  else if (started){
    inData[index] = aChar;
    index++;
    inData[index] = '\0';
  }
}
if(newLine){
  cln = 0;
  newLine = false;
  upd = true;
}
if (started && ended){
  int inInt = atoi(inData);

  //do something wiht inInt
  inpt[cln] = inInt; 
  cln++;

  started = false;
  ended = false;
  index = 0;
  inData[index] = '\0';
}
  
  // put your main code here, to run repeatedly:

if (upd){ // if update is neccesary
  upd = false;
  
//for (int i  = 0; i<20; i++){
//Serial.println(inpt[i]);
//}

//for the fingers
for (int i = 5; i<10; i++) {
  posL[i] = ((maxL[i]-minL[i]) * (inpt[i + 10] / 100.0) + minL[i]);
  Serial.println(inpt[i+10]);
  Serial.println(minL[i]);
  Serial.println(maxL[i]);
  Serial.println(posL[i]);
}
for (int i = 5; i<10; i++){
  posR[i] = (-(maxR[i]-minR[i]) * (inpt[i + 5] / 100.0) + maxR[i]);
}
posR[6] = (maxR[6]-minR[6]) * (inpt[11] / 100.0) + minR[6];
posR[7] = (maxR[7]-minR[7]) * (inpt[12] / 100.0) + minR[7];

//for the rest
for (int i = 0; i<5; i++) {
  posR[i] = sgnR[i]*inpt[i]*conv+positionInitalR[i];
}
for (int i = 0; i<5; i++) {
  posL[i] = sgnL[i]*inpt[i+5]*conv+positionInitalL[i];
}

//for (int i = 0; i <10; i++){
//  Serial.println(posL[i]);
//}

for (int i = 0; i<10; i++){ ///make sure that this wont break
  if (posL[i]<minL[i]){
    posL[i] = minL[i];
  }
  if (posL[i]>maxL[i]){
    posL[i] = maxL[i];
  }
  if (posR[i]<minR[i]){
    posR[i] = minR[i];
  }
  if (posR[i]>maxR[i]){
    posR[i] = maxR[i];
  }
}

for (int i = 0; i<10;i++){
  leftHand.setPWM(i,0,posL[i]);
  rightHand.setPWM(i,0,posR[i]);
  }
}

}






