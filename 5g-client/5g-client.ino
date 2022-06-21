#include "include/config.h"
#include "include/http.h"
#include "include/led.h"

#include <Sodaq_LSM303AGR.h>
#include <Sodaq_UBlox_GPS.h>
#include <Wire.h>

#define ADC_AREF	3.3f
#define BATVOLT_R1	4.7f
#define BATVOLT_R2	10.0f
#define BATVOLT_PIN BAT_VOLT

#define statusDelay 1.0	   // seconds

#define batteryFactor (0.978 * (BATVOLT_R1 / BATVOLT_R2 + 1) / ADC_AREF)

http_client		http;
Sodaq_LSM303AGR accel;

void setup() {
	led.begin();
	http.begin();

	pinMode(BATVOLT_PIN, INPUT);
	pinMode(CHARGER_STATUS, INPUT);

	Wire.begin();
	delay(1000);
	sodaq_gps.init(GPS_ENABLE);

	accel.rebootAccelerometer();
	delay(1000);

	// Enable the Accelerometer
	accel.enableAccelerometer();
}

void loop() {
	led.blink();

	static int last = 0;
	int		   now	= millis();

	static double lat = 0, lon = 0, accuracy = 0;

	if (now - last > statusDelay * 1000) {
		if (sodaq_gps.scan(true, gpsTimeout * 1000)) {
			led.set(status_led::COLOR_GREEN);

			lat		 = sodaq_gps.getLat();
			lon		 = sodaq_gps.getLon();
			accuracy = 1.0 / sodaq_gps.getHDOP() * 100;
			// -> 100% the best, 0% the worst
		} else {
			led.set(status_led::COLOR_BLUE);
		}

		json req;
		//	req.method				= "POST";
		//	req.endpoint			= "/api/update";
		req["latitude"]	   = lat;
		req["longitude"]   = lon;
		req["accuracy"]	   = accuracy;
		req["battery"]	   = batteryVoltage();
		req["temperature"] = temperature();
		req["charging"]	   = (bool) digitalRead(CHARGER_STATUS);

		http.send(http_client::HTTP_POST, "/api/update", req);
		last = now;
	}
}

int temperature() {
	return accel.getTemperature();
}

int batteryVoltage() {
	return batteryFactor * (float) analogRead(BATVOLT_PIN);
}
