#include "include/config.h"
#include "include/modem.h"
#include "include/passthrough.h"

#include <Sodaq_LSM303AGR.h>
#include <Sodaq_UBlox_GPS.h>

#define ADC_AREF	3.3f
#define BATVOLT_R1	4.7f
#define BATVOLT_R2	10.0f
#define BATVOLT_PIN BAT_VOLT

#define batteryFactor 0.978 / ADC_AREF*(BATVOLT_R1 / BATVOLT_R2 + 1)

// sara_modem		modem;
Sodaq_LSM303AGR accel;
passthrough		pass;

void setup() {
	// -*- hardware initiation -*-

	usbSerial.begin(baud);
	while (usbWait && !usbSerial)
		;

	pinMode(BATVOLT_PIN, INPUT);

	//	modem.init();
	pass.init();

	Wire.begin();
	delay(1000);
	sodaq_gps.init(GPS_ENABLE);

	accel.rebootAccelerometer();
	delay(1000);

	// Enable the Accelerometer
	accel.enableAccelerometer();

	pass.connect("muizenval.tk", 80);

	//	modem.send("ATE0");	   // disable command-echo

	// if (modem.send("AT+CPIN=\"" SIM_PIN "\"") == sara_modem::COMMAND_ERROR) {
	//	// usbSerial.println("[EROR] sim can't be unlocked, wrong PIN");
	//	return;
	// }
	// usbSerial.println(prefixInfo "sim successful unlocked");
	/*

	modem.send("AT+CPSMS=0");	  // Disable Power Saving Mode
	modem.send("AT+CEDRXS=0");	  // Disable eDRX
	// usbSerial.println(prefixInfo "disabled power safe");


		// -*- internet initialization -*-
		char info[100];

		modem.send("AT+CFUN=15", sara_modem::COMMAND_BLOCK);	   // Reset the module
		modem.send("AT+UMNOPROF=1", sara_modem::COMMAND_BLOCK);	   // Set MNO profile (1=automatic,100=standard europe)
		modem.send("AT+URAT?", info);
		// usbSerial.print(prefixInfo "urat: ");
		// usbSerial.println(info);
		modem.send("AT+URAT=8", sara_modem::COMMAND_IGNORE);							// Set URAT to LTE-M/NB-IOT
		modem.send("AT+CEREG=3", sara_modem::COMMAND_IGNORE);							// Enable URCs
		modem.send("AT+CGDCONT=1,\"IP\",\"" simAPN "\"", sara_modem::COMMAND_BLOCK);	// Set the APN
		modem.send("AT+CFUN=1");														// enable radio
		modem.send("AT+COPS=0,2", sara_modem::COMMAND_BLOCK);							// Autoselect the operator

		// usbSerial.print(prefixInfo "waiting for connection");

		char response[100];

		// Check Siganl strenght, repeat till you have a valid CSQ (99,99 means no signal)
		while (modem.send("AT+CSQ", response, sara_modem::COMMAND_SILENT) == sara_modem::COMMAND_OK && !strcmp(response, "+CSQ: 99,99")) {
			delay(1000);
			// usbSerial.print(".");
		}

		// Wait for attach, 1 = attached
		while (modem.send("AT+CGATT?", response, sara_modem::COMMAND_SILENT) == sara_modem::COMMAND_OK && strcmp(response, "+CGATT: 1")) {
			delay(1000);
			// usbSerial.print(".");
		}
		// usbSerial.println();

		// usbSerial.println(prefixInfo "connected!");

		// -*- server connection -*-


	//AT+UHTTP=0,0,"86.92.67.21"
	//AT+UHTTP=0,5,80
	//AT+UHTTPC=0,5,"/api/search_connect","","TEST!",1

		modem.send("AT+UHTTP=0,0,\"86.92.67.21\"");
		modem.send("AT+UHTTP=0,5,80");
		modem.send("AT+UHTTPC=0,5,\"/api/search_connect\",\"\",\"TEST!\",1");*/


	// usbSerial.println(prefixInfo "initiation completed, starting passthrough:");
}


void loop() {
	/*	// -*- passthrough for custom commands -*-
		while (usbSerial.available())
			modemSerial.write(usbSerial.read());

		while (modemSerial.available())
			usbSerial.write(modemSerial.read());

		char buffer[512];
		gps.read(buffer);

		if (buffer[0] != '\0') {
			// usbSerial.print("gps   | ");
			// usbSerial.println(buffer);
		}*/

	static double lat = 0, lon = 0, accuracy = 0;

	if (sodaq_gps.scan(true, 10000)) {
		lat		 = sodaq_gps.getLat();
		lon		 = sodaq_gps.getLon();
		accuracy = 1.0 / sodaq_gps.getHDOP() * 100;
		// -> 100% the best, 0% the worst
		// usbSerial.print(sodaq_gps.getLat(), 13);
		// usbSerial.print(" - ");
		// usbSerial.print(sodaq_gps.getLon(), 13);
		// usbSerial.print(" ~ accuracy ");
		// usbSerial.print(1.0 / sodaq_gps.getHDOP() * 100, 1);
		// usbSerial.println("%");
	}

	passthrough::http_packet req, res;
	req.method				= "POST";
	req.endpoint			= "/api/update";
	req.body["latitude"]	= lat;
	req.body["longitude"]	= lon;
	req.body["accuracy"]	= accuracy;
	req.body["battery"]		= batteryVoltage();
	req.body["temperature"] = temperature();

	pass.send(req);

	// usbSerial.print(batteryVoltage());
	// usbSerial.println("V battery");

	// usbSerial.print(temperature());
	// usbSerial.println(" deg celsius");
}

int temperature() {
	return accel.getTemperature();
}

int batteryVoltage() {
	return batteryFactor * (float) analogRead(BATVOLT_PIN);
}
