/*
 * SimpleReceiver.cpp
 *
 * Demonstrates receiving NEC IR codes with IRrecv
 *
 *  Copyright (C) 2020-2021  Armin Joachimsmeyer
 *  armin.joachimsmeyer@gmail.com
 *
 *  This file is part of Arduino-IRremote https://github.com/Arduino-IRremote/Arduino-IRremote.
 *
 *  
 * OBS:ONLY up, Down, left, right is actions is supported now. 
 *
 */

#include <Arduino.h>
#include <stdint.h>

/*
 * Define macros for input and output pin etc.
 */
#include "PinDefinitionsAndMore.h"
#include <IRremote.h>
#define DECODE_NEC

/*
* Receiced Hexadecimal values, when a button is push on the remote controller. 
*/
uint16_t commandStar = 0x16; 
uint16_t commandHashtag = 0xD; 
uint16_t commandOk = 0x1C; 

uint16_t commandUp = 0x18; 
uint16_t commandDown = 0x52; 
uint16_t commandLeft = 0x8; 
uint16_t commandRight = 0x5A; 

uint16_t commandZero = 0x19; 
uint16_t commandOne = 0x45; 
uint16_t commandTwo = 0x46; 
uint16_t commandThree = 0x47; 
uint16_t commandFour = 0x44; 
uint16_t commandFive = 0x40; 
uint16_t commandSix = 0x43;
uint16_t commandSeven = 0x7; 
uint16_t commandEight = 0x15;
uint16_t commandNine = 0x9;

/*
* 
* Variables functions, to stored the function that should be executed, when a button i clicked. 
*/ 
void (*actionCommandStar)(void); // definere en variable for en functions handling.
void (*actionCommandHashtag)(void); // definere en variable for en functions handling.
void (*actionCommandOk)(void); // definere en variable for en functions handling.

void (*actionCommandUp)(void); // definere en variable for en functions handling.
void (*actionCommandDown)(void); // definere en variable for en functions handling.
void (*actionCommandLeft)(void); // definere en variable for en functions handling.
void (*actionCommandRight)(void); // definere en variable for en functions handling.

void (*actionCommandZero)(void); // definere en variable for en functions handling.
void (*actionCommandOne)(void); // definere en variable for en functions handling.
void (*actionCommandTwo)(void); // definere en variable for en functions handling.
void (*actionCommandThree)(void); // definere en variable for en functions handling.
void (*actionCommandFour)(void); // definere en variable for en functions handling.
void (*actionCommandFive)(void); // definere en variable for en functions handling.
void (*actionCommandSix)(void); // definere en variable for en functions handling.
void (*actionCommandSeven)(void); // definere en variable for en functions handling.
void (*actionCommandEight)(void); // definere en variable for en functions handling.
void (*actionCommandNine)(void); // definere en variable for en functions handling.

/**
*
* Setter functions for our variale functions. 
*/
void SetActionCommandStar(void (*ptr)(void))    { actionCommandStar =ptr; }
void SetActionCommandHashtag(void (*ptr)(void)) { actionCommandHashtag =ptr; }
void SetActionCommandOk(void (*ptr)(void))      { actionCommandOk =ptr; }

void SetActionCommandDown(void (*ptr)(void))  { actionCommandDown =ptr; }
void SetActionCommandUp(void (*ptr)(void))    { actionCommandUp =ptr; }
void SetActionCommandLeft(void (*ptr)(void))  { actionCommandLeft =ptr; }
void SetActionCommandRight(void (*ptr)(void)) { actionCommandRight =ptr; }

void SetActionCommandZero(void (*ptr)(void))  { actionCommandZero =ptr; }
void SetActionCommandOne(void (*ptr)(void))   { actionCommandOne =ptr; }
void SetActionCommandTwo(void (*ptr)(void))   { actionCommandTwo =ptr; }
void SetActionCommandThree(void (*ptr)(void)) { actionCommandThree =ptr; }
void SetActionCommandFour(void (*ptr)(void))  { actionCommandFour =ptr; }
void SetActionCommandFive(void (*ptr)(void))  { actionCommandFive =ptr; }
void SetActionCommandSix(void (*ptr)(void))   { actionCommandSix =ptr; }
void SetActionCommandSeven(void (*ptr)(void)) { actionCommandSeven =ptr; }
void SetActionCommandEight(void (*ptr)(void)) { actionCommandEight =ptr; }
void SetActionCommandNine(void (*ptr)(void))  { actionCommandNine =ptr; }


/**
* Execute method that are registered in the loop function. 
*/
void ExecuteRemoteAction(uint16_t action) 
{ 
        if(action == commandStar)     {(*actionCommandStar)();
  }else if(action == commandHashtag)  {(*actionCommandHashtag)();
  }else if(action == commandOk)       { (*actionCommandOk)();

  }else if(action == commandDown)     {(*actionCommandDown)();
  }else if(action == commandUp)       {(*actionCommandUp)();
  }else if(action == commandLeft)     {(*actionCommandLeft)();
  }else if(action == commandRight)    {(*actionCommandRight)();
  
  }else if(action == commandZero)     {(*actionCommandZero)();
  }else if(action == commandOne)      {(*actionCommandOne)();
  }else if(action == commandTwo)      {(*actionCommandTwo)();
  }else if(action == commandThree)    {(*actionCommandThree)();
  }else if(action == commandFour)     {(*actionCommandFour)();
  }else if(action == commandFive)     {(*actionCommandFive)();
  }else if(action == commandSix)      {(*actionCommandSix)();
  }else if(action == commandSeven)    {(*actionCommandSeven)();
  }else if(action == commandEight)    {(*actionCommandEight)();
  }else if(action == commandNine)     {(*actionCommandNine)();
  }
}

void ReceiverSetup() {
    //Serial.begin(9600);
    // Just to know which program is running on my Arduino
    Serial.println("setting up remoteController");
    Serial.println(F("START " __FILE__ " from " __DATE__ "\r\nUsing library version " VERSION_IRREMOTE));
    /*
     * Start the receiver, enable feedback LED and take LED feedback pin from the internal boards definition
     */
    IrReceiver.begin(IR_RECEIVE_PIN, ENABLE_LED_FEEDBACK, USE_DEFAULT_FEEDBACK_LED_PIN);

    Serial.print(F("Ready to receive IR signals at pin "));
    Serial.println(IR_RECEIVE_PIN);
}


void RecevierLoop() {
    /*
     * Check if received data is available and if yes, try to decode it.
     * Decoded result is in the IrReceiver.decodedIRData structure.
     *
     * E.g. command is in IrReceiver.decodedIRData.command
     * address is in command is in IrReceiver.decodedIRData.address
     * and up to 32 bit raw data in IrReceiver.decodedIRData.decodedRawData
     */
    if (IrReceiver.decode()) {

        // Print a short summary of received data
        //IrReceiver.printIRResultShort(&Serial); // Optional
        
        if (IrReceiver.decodedIRData.protocol == UNKNOWN) {
            // We have an unknown protocol here, so do nothing.
  
        } else {
          // Method for execute Capture action:
          ExecuteRemoteAction(IrReceiver.decodedIRData.command); 
        }
          IrReceiver.resume(); // Enable receiving of the next value
    }
}
