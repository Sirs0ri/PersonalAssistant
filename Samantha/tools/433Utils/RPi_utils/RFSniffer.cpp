/*
  RF_Sniffer
  
  Hacked from http://code.google.com/p/rc-switch/
  
  by @justy to provide a handy RF code sniffer
*/

#include "RCSwitch.h"
#include <stdlib.h>
#include <stdio.h>
#include <sstream>
#include <string.h>
     
     
RCSwitch mySwitch;
 


int main(int argc, char *argv[]) {
  
     // This pin is not the first pin on the RPi GPIO header!
     // Consult https://projects.drogon.net/raspberry-pi/wiringpi/pins/
     // for more information.
     int PIN = 2;
     
     if(wiringPiSetup() == -1)
       return 0;

     mySwitch = RCSwitch();
     mySwitch.enableReceive(PIN);  // Receiver on inerrupt 0 => that is pin #2
     
    
     while(1) {
  
      if (mySwitch.available()) {
    
        int value = mySwitch.getReceivedValue();
    
        if (value == 0) {
          printf("Unknown encoding\n");
        } else {    
	  char integer_string[32];
	  int integer = mySwitch.getReceivedValue();
	  sprintf(integer_string, "%d", integer);
	  char other_string[128] = "curl -G '127.0.0.1:5000/' --data-urlencode 'key=433' --data-urlencode 'params=";
	  char yet_another_string[32] = "' >/dev/null 2>/dev/null";
	  strcat(other_string, integer_string);
	  strcat(other_string, yet_another_string);
	  system(other_string);
          printf("Received %i\n", mySwitch.getReceivedValue() );
        }
    
        mySwitch.resetAvailable();
    
      }
      
  
  }

  exit(0);


}

