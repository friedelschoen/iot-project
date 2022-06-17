#include "include/config.h"
#include "include/modem.h"


void sara_modem::init() {
	pinMode(modemPowerPin, OUTPUT);		 // Put voltage on the nb-iot module
	pinMode(modemVoltagePin, OUTPUT);	 // Switch module voltage
	pinMode(modemEnablePin, OUTPUT);	 // Set state to active

	digitalWrite(modemPowerPin, HIGH);
	digitalWrite(modemVoltagePin, LOW);
	digitalWrite(modemEnablePin, HIGH);
	modemSerial.begin(baud);

	while (!modemSerial)
		;

	// -*- module initialization -*-
	// usbSerial.print(prefixInfo "waiting for module to start up");
	for (;;) {
		// usbSerial.print('.');
		modemSerial.write("AT\r\n");
		delay(1000);
		if (modemSerial.available())
			break;
	}

	while (modemSerial.available())	   // clear cache
		modemSerial.read();
	// usbSerial.println();
}

sara_modem::command_status sara_modem::send(const char* request, char* response, command_flags flags) {
	char   line[lineBuffer];
	size_t lineLen;
	char   buf;

	bool silent		  = flags & COMMAND_SILENT,
		 block		  = flags & COMMAND_BLOCK,
		 ignore		  = flags & COMMAND_IGNORE,
		 event_handle = flags & COMMAND_EVENT;

	if (response)
		response[0] = '\0';

	unsigned long start = millis(),
				  now;

	modemSerial.write(request);
	modemSerial.write("\r\n");
	modemSerial.flush();

	if (blockDebug && block && !silent) {
		// usbSerial.print(prefixDebug "command '");
		// usbSerial.print(request);
		// usbSerial.println("' is blocking");
	}

	for (;;) {
		lineLen = 0;
		for (;;) {
			while (!modemSerial.available()) {
				now = millis();
				if (ignore && now - start > ignoreDelay * 1000) {
					if (commandDebug && !silent) {
						// usbSerial.print(prefixDebug "command '");
						// usbSerial.print(request);
						// usbSerial.println("' succeed (ignoring response)");
					}
					return COMMAND_TIMEOUT;
				} else if (!ignore && !block && now - start > commandTimeout * 1000) {
					if (commandDebug && !silent) {
						// usbSerial.print(prefixWarn "command '");
						// usbSerial.print(request);
						// usbSerial.println("' timed out");
					}
					return COMMAND_TIMEOUT;
				}
			}
			buf = modemSerial.read();
			if (buf == '\r')
				continue;
			if (buf == '\n')
				break;
			line[lineLen++] = buf;
		}
		line[lineLen] = '\0';

		if (String(line) == "OK") {
			if (commandDebug && !silent) {
				// usbSerial.print(prefixDebug "command '");
				// usbSerial.print(request);
				// usbSerial.println("' succeed");
			}
			return COMMAND_OK;
		} else if (strstr(line, "ERROR")) {
			if (commandDebug && !silent) {
				// usbSerial.print(prefixError "command '");
				// usbSerial.print(request);
				// usbSerial.println("' failed");
			}
			return COMMAND_ERROR;
		} else if (event_handle && line[0] == '+') {
			if (eventDebug && !silent) {
				// usbSerial.print(prefixEvent "event '");
				// usbSerial.print(line);
				// usbSerial.println(" caused'");
			}
		} else if (line[0] != '\0' && strcmp(request, line)) {
			if (lineDebug && !silent) {
				// usbSerial.print(prefixLine);
				// usbSerial.print(request);
				// usbSerial.print(" -> '");
				// usbSerial.print(line);
				// usbSerial.println("'");
			}

			if (response) {
				if (response[0] != '\0')	// check if not empty string
					strcat(response, "\n");
				strcat(response, line);
			}
		}
	}
	delay(commandDelay * 1000);	   // wait 0.1 sec
}

sara_modem::command_status sara_modem::send(const char* request, command_flags flags) {
	return send(request, NULL, flags);
}
