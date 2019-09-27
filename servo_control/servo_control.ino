#include <Servo.h>
/*
 * Kontrola nad serwam do zasłaniania luster
 * 
 */
String commandString="";
boolean stringComplete = false;

Servo servomotors[4];
int servopins[4]={8,9,10,11};
int servopositions[4]={90,90,90,90};

void serialEvent(){
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read();
    
    // add it to the inputString:
    if (inChar != '\n')
      commandString += inChar;
      //Serial.println(commandString);
    
    // if the incoming character is a newline, set a flag
    // so the main loop can do something about it:
    if (inChar == '\n'){
      commandString.toUpperCase();
    //  Serial.println(commandString);
      stringComplete = true;
    }
  }

  if(stringComplete){
    Serial.println(commandString.substring(0,11));
  //  Serial.println(String(commandString.substring(11).toInt()+10));
    
    if(commandString.substring(0,5)=="TURN:"){
      servopositions[String(commandString[5]).toInt()-1]=commandString.substring(7).toInt();
    }
    //servopositions[0]=commandString.toInt();
    commandString="";
    stringComplete=false;
   }
}

void setup() {
  Serial.begin(9600);
  for(int i=0;i<4;i++){
    servomotors[i].attach(servopins[i]);
  }
}

void loop() {
  for(int i=0;i<4;i++){
    servomotors[i].write(servopositions[i]);
  }
  delay(30);
}
