#pragma once

// -*- hardware stuff -*-
#define usbSerial		SerialUSB			// usb serial port
#define modemSerial		Serial1				// modem serial port
#define modemPowerPin	SARA_ENABLE			// modem power pin
#define modemEnablePin	SARA_TX_ENABLE		// modem enable pin
#define modemVoltagePin SARA_R4XX_TOGGLE	// modem voltage pin

// -*- behaviour settings -*-
#define remoteBaut		   115200	 // baut-rate of modem-/usb-serial
#define remoteFirstTimeout 5.0		 // seconds to wait for the first timeout
#define remoteTimeout	   1.0		 // seconds to wait for remote to timeout
#define lineBuffer		   512		 // buffer-size (bytes) to use to store lines
#define commandTimeout	   10.0		 // seconds to cancel a command
#define commandDelay	   0.1		 // delay after every command
#define ignoreDelay		   2.0		 // seconds to wait if command is run with COMMAND_IGNORE
#define commandDebug	   true		 // send debug information about command requests
#define eventDebug		   true		 // print '+'-events
#define lineDebug		   false	 // print each line to debug
#define blockDebug		   true		 // print if command is blocking
#define usbWait			   true		 // wait for a usb-connection

// -*- sim settings -*-
#define macAddress "CAFEBABE01234567"	  // the boards mac-address
#define simPin	   "0000"				  // PIN of the sim
#define simAPN	   "lpwa.vodafone.iot"	  // APN-network of the sim

// -*- prefixes -*-
#define prefixInfo	"info  | "
#define prefixDebug "debug | "
#define prefixError "error | "
#define prefixLine	"line  | "
#define prefixWarn	"warn  | "
#define prefixEvent "event | "
