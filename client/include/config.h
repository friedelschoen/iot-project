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
#define gpsTimeout		   15		 // seconds to gps-timeout
#define statusInterval	   5		 // send status every n seconds

#define ADC_AREF	  3.3f
#define BATVOLT_R1	  4.7f
#define BATVOLT_R2	  10.0f
#define BATVOLT_PIN	  BAT_VOLT
#define batteryFactor (0.978 * (BATVOLT_R1 / BATVOLT_R2 + 1) / ADC_AREF)


struct configuration {
	bool valid;

	char token[17];
	char domain[50];

	void open();
	void save();
};

extern FlashStorageClass<configuration> config_flash;

extern configuration config_default;
extern configuration config;
