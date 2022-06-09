#include "command.h"
#include "config.h"

// -*- helper functions -*-
command_status sendCommand(const char* request, char* response, command_flags flags) {
	char   line[lineBuffer];
	size_t lineLen;
	char   buf;

	bool silent		  = flags & COMMAND_SILENT,
		 block		  = flags & COMMAND_BLOCK,
		 event_handle = flags & COMMAND_EVENT;

	if (response)
		response[0] = '\0';

	unsigned long start = millis(),
				  now;

	modemSerial.write(request);
	modemSerial.write("\r\n");
	modemSerial.flush();

	if (blockDebug && block && !silent) {
		usbSerial.print("[DBUG] command '");
		usbSerial.print(request);
		usbSerial.println("' is blocking");
	}

	for (;;) {
		lineLen = 0;
		for (;;) {
			while (!modemSerial.available()) {
				now = millis();
				if (!block && now - start > commandTimeout * 1000) {
					if (commandDebug && !silent) {
						usbSerial.print("[WARN] command '");
						usbSerial.print(request);
						usbSerial.println("' timed out");
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
				usbSerial.print("[DBUG] command '");
				usbSerial.print(request);
				usbSerial.println("' succeed");
			}
			return COMMAND_OK;
		} else if (strstr(line, "ERROR")) {
			if (commandDebug && !silent) {
				usbSerial.print("[WARN] command '");
				usbSerial.print(request);
				usbSerial.println("' failed");
			}
			return COMMAND_ERROR;
		} else if (event_handle && line[0] == '+') {
			if (eventDebug && !silent) {
				usbSerial.print("[EVNT] event '");
				usbSerial.print(line);
				usbSerial.println(" caused'");
			}
		} else if (line[0] != '\0' && strcmp(request, line)) {
			if (lineDebug && !silent) {
				usbSerial.print("[LINE] ");
				usbSerial.print(request);
				usbSerial.print(" -> '");
				usbSerial.print(line);
				usbSerial.println("'");
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

command_status sendCommand(const char* request, command_flags flags) {
	return sendCommand(request, NULL, flags);
}
