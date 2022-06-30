#pragma once

#include <FlashStorage.h>

// -*- hardware stuff -*-
#define usbSerial		SerialUSB			// usb serial port
#define modemSerial		Serial1				// modem serial port
#define modemPowerPin	SARA_ENABLE			// modem power pin
#define modemEnablePin	SARA_TX_ENABLE		// modem enable pin
#define modemVoltagePin SARA_R4XX_TOGGLE	// modem voltage pin
#define batteryPin		BAT_VOLT			// messuring battery
#define chargerPin		CHARGER_STATUS		// messuring charging
#define ledRed			LED_RED				// rgb-led (red)
#define ledGreen		LED_GREEN			// rgb-led (green)
#define ledBlue			LED_BLUE			// rgb-led (blue)
#define trapPin			10					// pin of magnet-sensor

// -*- behaviour settings -*-
#define remoteBaud	 115200	   // baud-rate of usb-serial
#define modemBaud	 115200	   // baud-rate of modem-serial
#define remoteForce	 true	   // do not try connect to modem
#define lineBuffer	 512	   // buffer-size (bytes) to use to store lines
#define commandDebug true	   // send debug information about command requests
#define eventDebug	 true	   // print '+'-events
#define lineDebug	 false	   // print each line to debug
#define blockDebug	 true	   // print if command is blocking

// -*- timing settings (seconds) -*-
#define remoteFirstTimeout 5	  // seconds to wait for the first timeout
#define remoteTimeout	   1	  // seconds to wait for remote to timeout
#define commandTimeout	   10	  // seconds to cancel a command
#define commandDelay	   0.1	  // delay after every command
#define ignoreDelay		   2	  // seconds to wait if command is run with COMMAND_IGNORE
#define gpsTimeout		   20	  // seconds to gps-timeout
#define statusInterval	   10	  // send status every n seconds
#define loopDelay		   5	  // seconds to wait each loop()

// -*- battery stuff -*-
#define adcAREF		  3.3
#define batteryR1	  4.7
#define batteryR2	  10.0
#define batteryFactor (0.978 * (batteryR1 / batteryR2 + 1) / adcAREF)


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
