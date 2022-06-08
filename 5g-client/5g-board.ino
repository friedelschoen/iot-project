// -*- utilities -*-
#define usbSerial	SerialUSB
#define modemSerial Serial1
#define powerPin	SARA_ENABLE
#define enablePin	SARA_TX_ENABLE
#define voltagePin	SARA_R4XX_TOGGLE


// -*- settings -*-
#define baud		   115200	 // baut-rate of modem-/usb-serial
#define lineBuffer	   256		 // buffer-size (bytes) to use to store lines
#define commandTimeout 5.0		 // seconds to cancel a command
#define commandDelay   0.1		 // delay after every command
#define commandDebug   true		 // send debug information about command requests
#define eventHandling  false	 // handle '+'-events different
#define eventDebug	   true		 // print '+'-events
#define lineDebug	   true		 // print each line to debug


// -*- enums -*-
enum command_status {
	COMMAND_OK,
	COMMAND_ERROR,
	COMMAND_TIMEOUT
};

#define SIM_PIN "0000"
//#define APN_DOMAIN "live.vodafone.com"
#define APN_DOMAIN "nb.inetd.gdsp"

// -*- helper functions -*-

/** command_status sendCommand(const char* requst, char* response)
 * sends `request` to 5G and stores its response in `response` (may be NULL'ed)
 *
 * if the command succeed, COMMAND_OK will be returned
 * if the command failed, COMMAND_ERROR will be returned
 * if the command timed out, COMMAND_TIMEOUT will be returned (took longer than `commandTimeout`)
 */
command_status sendCommand(const char* request, char* response, bool silent = false) {
	char   line[lineBuffer];
	size_t lineLen;
	char   buf;

	if (response)
		response[0] = '\0';

	unsigned long start = millis(),
				  now;

	modemSerial.write(request);
	modemSerial.write("\r\n");
	modemSerial.flush();

	for (;;) {
		lineLen = 0;
		for (;;) {
			while (!modemSerial.available()) {
				now = millis();
				if (now - start > commandTimeout * 1000) {
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
		} else if (eventHandling && line[0] == '+') {	 // additional info
			if (eventDebug) {
				usbSerial.print("[EVNT] event '");
				usbSerial.print(line);
				usbSerial.println(" caused'");
			}
		} else if (line[0] != '\0') {
			if (lineDebug) {
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

int sendCommand(const char* request, bool silent = false) {
	return sendCommand(request, NULL, silent);
}


void setup() {
	pinMode(powerPin, OUTPUT);		// Put voltage on the nb-iot module
	pinMode(voltagePin, OUTPUT);	// Switch module voltage
	pinMode(enablePin, OUTPUT);		// Set state to active

	digitalWrite(powerPin, HIGH);
	digitalWrite(voltagePin, LOW);
	digitalWrite(enablePin, HIGH);

	usbSerial.begin(baud);
	while (!usbSerial)
		;

	modemSerial.begin(baud);
	while (!modemSerial)
		;


	usbSerial.print("[INFO] waiting for module to start up");
	for (;;) {
		usbSerial.print('.');
		modemSerial.write("AT\r\n");
		delay(1000);
		if (modemSerial.available())
			break;
	}
	while (modemSerial.available())	   // clear cache
		modemSerial.read();
	usbSerial.println();

	sendCommand("ATE0");	// disable command-echo

	char info[256];
	sendCommand("ATI", info);

	usbSerial.println("[INFO] module information:");
	usbSerial.println(info);

	//	if (sendCommand("AT+CPIN=\"" SIM_PIN "\"") == COMMAND_ERROR) {
	//		usbSerial.println("[EROR] sim can't be unlocked, wrong PIN");
	//		return;
	//	}
	usbSerial.println("[INFO] SIM unlocked");

	sendCommand("AT+CPSMS=0");	   // Disable Power Saving Mode
	sendCommand("AT+CEDRXS=0");	   // Disable eDRX
	usbSerial.println("[INFO] disable power safe");


	sendCommand("AT+CFUN=15");								  // Reset the module
	sendCommand("AT+UMNOPROF=1");							  // Set MNO profile (1=automatic,100=standard europe)
	sendCommand("AT+URAT=7");								  // Set URAT to LTE-M
	sendCommand("AT+CEREG=3");								  // Enable URCs
	sendCommand("AT+CGDCONT=1,\"IP\",\"" APN_DOMAIN "\"");	  // Set the APN
	sendCommand("AT+COPS=0,2");								  // Autoselect the operator

	//	usbSerial.println("[INFO] waiting for connection...");

	/*	char response[100];
		while (sendCommand("AT+CSQ", response, true) == COMMAND_OK && strcmp(response, "+CSQ: 99,99"))
			;
		// Check Siganl strenght, repeat till you have a valid CSQ (99,99 means no signal)
		while (sendCommand("AT+CGATT?", response, true) == COMMAND_OK && !strcmp(response, "+CGATT: 1"))
			;
		// Check Siganl strenght, repeat till you have a valid CSQ (99,99 means no signal)

		usbSerial.println("Connected!");*/

	usbSerial.println("[INFO] initiation completed, starting passthrough:");
}

void loop() {
	while (usbSerial.available())
		modemSerial.write(usbSerial.read());

	while (modemSerial.available())
		usbSerial.write(modemSerial.read());
}
