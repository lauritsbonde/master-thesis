#include <Servo.h>

// servo range: 0-1023
Servo ServoLeft; 
Servo ServoRight; 

int servoPin_left = 9;
int servoPin_right = 10;
int buttonPin = 36; 
int light = 38; 


void ServoSetup() {
  ServoLeft.write(90);  // Stop, 
}
// Stop the boat
void MethodforLeftControl(void) {
  Serial.println("called command left");
   ServoLeft.write(90); 
   ServoRight.write(90); 
   stopLogging();
}
// Start the boat
void MethodforRightControl(void) {
  Serial.println("called command Right");
  ServoLeft.write(180); // 91-180, where 180 is full speed forward, 0 is full speed backward. 
  ServoRight.write(180); // 91-180, where 180 is full speed forward, 0 is full speed backward. 
  startLogging();
  
}

void MethodForOneControl(void) {
  Serial.println("called command One");
  startLogging();
  
  ServoLeft.write(100); // 91-180, where 180 is full speed forward, 0 is full speed backward. 
  ServoRight.write(100); // 91-180, where 180 is full speed forward, 0 is full speed backward. 
  
  delay(3000);
  ServoLeft.write(90); // 91-180, where 180 is full speed forward, 0 is full speed backward. 
  ServoRight.write(90); // 91-180, where 180 is full speed forward, 0 is full speed backward. 
}

void MethodForTwoControl(void) {
   Serial.println("called command One");
  int motorSpeed = 90;
  //ServoRight.write(180); // 91-180, where 180 is full speed forward, 0 is full speed backward. 
  startLogging();
  for(int i = 0; i <9; i++) {
    motorSpeed = motorSpeed + 10; 
    ServoLeft.write(motorSpeed); // 91-180, where 180 is full speed forward, 0 is full speed backward. 
    ServoRight.write(motorSpeed); // 91-180, where 180 is full speed forward, 0 is full speed backward. 
    delay(500); // delay 0.5 seconds
  }
 
  delay(3000); // run full speed for 3 seconds
  ServoLeft.write(90); // 91-180, where 180 is full speed forward, 0 is full speed backward. 
  ServoRight.write(90); // 91-180, where 180 is full speed forward, 0 is full speed backward. 
  stopLogging();
}




void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  

  pinMode(buttonPin, OUTPUT);
  pinMode(light, OUTPUT);
  
  // Setup Servo; 
  ServoLeft.attach(servoPin_left, 1000, 2000);
  ServoRight.attach(servoPin_right, 1000, 2000);
  //ServoSetup();

  SetActionCommandLeft(MethodforLeftControl); // register method for pushing down button. 
  SetActionCommandRight(MethodforRightControl); 
  SetActionCommandOne(MethodForOneControl);
  SetActionCommandTwo(MethodForTwoControl);


  ReceiverSetup(); // Execute setup for remoteController; 

  //ServoLeft.write(0);  Run this line, if the motor wont run, to set the ESC into main state. 

  SDWriterSetup();


}

void loop() {
  // put your main code here, to run repeatedly:

    //RecevierLoop(); // Run recevier function. 
    //loggingLoop(); // run Loggings function. 
    if(digitalRead(buttonPin) == 1) {
      digitalWrite(light, HIGH);
      delay(10000);
      MethodForOneControl();
      digitalWrite(light, LOW);
    };
    

}
