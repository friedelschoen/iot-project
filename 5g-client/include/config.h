#pragma once

// -*- hardware stuff -*-
#define usbSerial SerialUSB

// -*- behaviour settings -*-
#define baud		   115200	 // baut-rate of modem-/usb-serial
#define lineBuffer	   512		 // buffer-size (bytes) to use to store lines
#define commandTimeout 10.0		 // seconds to cancel a command
#define commandDelay   0.1		 // delay after every command
#define ignoreDelay	   2		 // seconds to wait if command is run with COMMAND_IGNORE
#define commandDebug   true		 // send debug information about command requests
#define eventDebug	   true		 // print '+'-events
#define lineDebug	   false	 // print each line to debug
#define blockDebug	   true		 // print if command is blocking
#define usbWait		   true		 // wait for a usb-connection

// -*- sim settings -*-
#define simPin "0000"				  // PIN of the sim
#define simAPN "lpwa.vodafone.iot"	  // APN-network of the sim

// -*- prefixes -*-
#define prefixInfo	"info  | "
#define prefixDebug "debug | "
#define prefixError "error | "
#define prefixLine	"line  | "
#define prefixWarn	"warn  | "
#define prefixEvent "event | "
