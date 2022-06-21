#include "include/config.h"
#include "include/led.h"

static bool colors[][3] = {
	[status_led::COLOR_NONE]	= { 0, 0, 0 },
	[status_led::COLOR_RED]		= { 1, 0, 0 },
	[status_led::COLOR_GREEN]	= { 0, 1, 0 },
	[status_led::COLOR_BLUE]	= { 0, 0, 1 },
	[status_led::COLOR_YELLOW]	= { 1, 1, 0 },
	[status_led::COLOR_CYAN]	= { 0, 1, 1 },
	[status_led::COLOR_MAGENTA] = { 1, 0, 1 },
	[status_led::COLOR_WHITE]	= { 1, 1, 1 },
};

static void writeLED(bool red, bool green, bool blue) {
	digitalWrite(LED_RED, !red);
	digitalWrite(LED_GREEN, !green);
	digitalWrite(LED_BLUE, !blue);
}

void status_led::begin() {
	pinMode(LED_RED, OUTPUT);
	pinMode(LED_GREEN, OUTPUT);
	pinMode(LED_BLUE, OUTPUT);
}

void status_led::set(color c) {
	color0 = color1 = c;
}

void status_led::set(color c0, color c1) {
	color0 = c0;
	color1 = c1;
}

void status_led::blink() {
	static int	last  = 0;
	static bool first = false;
	int			now	  = millis();

	if (now - last > blinkInterval * 1000) {
		if (first)
			writeLED(colors[color0][0], colors[color0][1], colors[color0][2]);
		else
			writeLED(colors[color1][0], colors[color1][1], colors[color1][2]);
		first = !first;
		last  = now;
	}
}

status_led led;