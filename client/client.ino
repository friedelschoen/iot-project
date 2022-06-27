#include "include/config.h"
#include "include/interface.h"
#include "include/led.h"

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

	config_current = config_flash.read();

	client.begin();

	json req;
	//	req["mac"] = macAddress;
	client.send(interface::METHOD_POST, "/api/hello", req);

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
		json gps;
		if (sodaq_gps.scan(true, gpsTimeout * 1000)) {
			gps["signal"]	 = true;
			gps["latitude"]	 = sodaq_gps.getLat();
			gps["longitude"] = sodaq_gps.getLon();
			gps["accuracy"]	 = getAccuracy();	 // -> 100% the best, 0% the worst
		} else {
			gps["signal"] = false;
		}

		gps["satellites"] = sodaq_gps.getNumberOfSatellites();

		json req;
		req["battery"]	   = batteryVoltage();
		req["temperature"] = accel.getTemperature();
		req["charging"]	   = getCharging();
		req["trap"]		   = getTrapStatus();
		req["gps"]		   = gps;

		client.send(interface::METHOD_POST, "/api/update", req);
		last = now;
	}
}

double batteryVoltage() {
	return batteryFactor * (double) analogRead(BATVOLT_PIN);
}

double getAccuracy() {
	double hdop = sodaq_gps.getHDOP();
	return hdop > 1 ? 1.0 / hdop * 100 : hdop * 100;
}

bool getTrapStatus() {
	return digitalRead(trapPin);
}

bool getCharging() {
	return digitalRead(CHARGER_STATUS);
}