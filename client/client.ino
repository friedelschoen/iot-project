#include "include/config.h"
#include "include/interface.h"
#include "include/led.h"
#include "include/macro.h"

#include <Sodaq_LSM303AGR.h>
#include <Sodaq_UBlox_GPS.h>
#include <Wire.h>

interface		client;
Sodaq_LSM303AGR accel;

void (*reset)() = 0;

void setup() {
	pinMode(LED_RED, OUTPUT);
	pinMode(LED_GREEN, OUTPUT);
	pinMode(LED_BLUE, OUTPUT);
	pinMode(trapPin, INPUT_PULLUP);
	pinMode(BATVOLT_PIN, INPUT);
	pinMode(CHARGER_STATUS, INPUT);

	config.open();
	client.begin();

	if (!config.valid)
		config = config_default;

	client.request["token"]	 = config.token;
	client.request["domain"] = config.domain;
	while (!client.send(interface::METHOD_POST, "/api/hello")) {
		writeLED(COLOR_RED);
		delay(500);
	}

	bool save = false;
	if (client.response.hasOwnProperty("token")) {
		strcpy(config.token, (const char*) client.response["token"]), save = true;
		json req;
		req["token"] = config.token;
		client.remote("set-token", req);
	}
	if (client.response.hasOwnProperty("domain"))
		strcpy(config.domain, (const char*) client.response["domain"]), save = true;


	if (save)
		config.save();


	Wire.begin();
	delay(1000);
	sodaq_gps.init(GPS_ENABLE);

	accel.rebootAccelerometer();
	delay(1000);

	// Enable the Accelerometer
	accel.enableAccelerometer();
}

void loop() {
	static int last = 0;
	int		   now	= millis();

	if (now - last > statusInterval * 1000) {
		if (sodaq_gps.scan(true, gpsTimeout * 1000)) {
			client.request["latitude"]	= sodaq_gps.getLat();
			client.request["longitude"] = sodaq_gps.getLon();
			client.request["accuracy"]	= getAccuracy();
		} else {
			client.request["latitude"]	= 0;
			client.request["longitude"] = 0;
			client.request["accuracy"]	= 0;
		}

		client.request["token"]		  = config.token;
		client.request["battery"]	  = batteryVoltage();
		client.request["temperature"] = accel.getTemperature();
		client.request["charging"]	  = getCharging();
		client.request["trap"]		  = getTrapStatus();
		client.request["satellites"]  = sodaq_gps.getNumberOfSatellites();

		client.send(interface::METHOD_POST, "/api/update");
		last = now;
	}
}

int batteryVoltage() {
	return batteryFactor * analogRead(BATVOLT_PIN);
}

double getAccuracy() {	  // -> 100% the best, 0% the worst
	double hdop = sodaq_gps.getHDOP();
	if (hdop > 1)
		hdop = 1.0 / hdop;
	return hdop * 100;
}

bool getTrapStatus() {
	return digitalRead(trapPin);
}

bool getCharging() {
	return digitalRead(CHARGER_STATUS);
}