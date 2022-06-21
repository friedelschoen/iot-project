#pragma once

#include <FlashStorage.h>

// -*- hardware stuff -*-
#define usbSerial		SerialUSB			// usb serial port
#define modemSerial		Serial1				// modem serial port
#define modemPowerPin	SARA_ENABLE			// modem power pin
#define modemEnablePin	SARA_TX_ENABLE		// modem enable pin
#define modemVoltagePin SARA_R4XX_TOGGLE	// modem voltage pin
#define trapPin			10					// pin of magnet-sensor

// -*- behaviour settings -*-
#define remoteBaud		   115200	 // baud-rate of usb-serial
#define modemBaud		   115200	 // baud-rate of modem-serial
#define remoteForce		   true		 // do not try connect to modem
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
#define blinkInterval	   0.25		 // seconds to wait for blink
#define gpsTimeout		   5		 // seconds to gps-timeout
#define statusInterval	   5		 // send status every n seconds

#define ADC_AREF	  3.3f
#define BATVOLT_R1	  4.7f
#define BATVOLT_R2	  10.0f
#define BATVOLT_PIN	  BAT_VOLT
#define batteryFactor (0.978 * (BATVOLT_R1 / BATVOLT_R2 + 1) / ADC_AREF)

// -*- sim settings -*-
//#define simPin		"0000"				   // PIN of the sim
//#define simAPN		"lpwa.vodafone.iot"	   // APN-network of the sim
//#define apiHostname "muizenval.tk"

// -*- prefixes -*-
#define prefixInfo	"info  | "
#define prefixDebug "debug | "
#define prefixError "error | "
#define prefixLine	"line  | "
#define prefixWarn	"warn  | "
#define prefixEvent "event | "


struct configuration {
	bool valid;

	char simPIN[4];
	char simPUK[8];
	char simAPN[50];
	char domain[50];

	char userToken[16];
};

extern FlashStorageClass<configuration> config_flash;

extern configuration config_default;
extern configuration config_current;
