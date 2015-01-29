int piston = 12;
char input;
void setup() {                
  pinMode(piston, OUTPUT);  
  Serial.begin(9600);  
}

// the loop routine runs over and over again forever:
void loop() {
  input=Serial.read();
  if(input==72){// 'H' // compressed spring
    digitalWrite(piston, HIGH);
    //Serial.println("GoingHigh");
  }
  if(input==76){// 'L'
    digitalWrite(piston, LOW);
    //Serial.println("GoingLow");
  }
  
}
