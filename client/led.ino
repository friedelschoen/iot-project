#include "include/led.h"

static const bool colors[][3] = {
	[COLOR_NONE]	= { 0, 0, 0 },
	[COLOR_RED]		= { 1, 0, 0 },
	[COLOR_GREEN]	= { 0, 1, 0 },
	[COLOR_BLUE]	= { 0, 0, 1 },
	[COLOR_YELLOW]	= { 1, 1, 0 },
	[COLOR_CYAN]	= { 0, 1, 1 },
	[COLOR_MAGENTA] = { 1, 0, 1 },
	[COLOR_WHITE]	= { 1, 1, 1 },
};

void writeLED(color c) {
	digitalWrite(LED_RED, !colors[c][0]);
	digitalWrite(LED_GREEN, !colors[c][1]);
	digitalWrite(LED_BLUE, !colors[c][2]);
}