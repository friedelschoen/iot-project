#define usbSerial	SerialUSB
#define modemSerial Serial1
#define powerPin	SARA_ENABLE
#define enablePin	SARA_TX_ENABLE
#define voltagePin	SARA_R4XX_TOGGLE
#define baud		115200

#define COMMAND_OK	  0
#define COMMAND_ERROR 1

#define LINE_BUFFER 256

#define SIM_PIN "0000"
//#define APN_DOMAIN "live.vodafone.com"
#define APN_DOMAIN "nb.inetd.gdsp"


size_t modemReadline(char* dest) {
	char   buf;
	size_t index = 0;

	for (;;) {
		while (!modemSerial.available())
			;
		buf = modemSerial.read();
		if (buf == '\r')
			continue;
		if (buf == '\n')
			break;
		dest[index++] = buf;
	}
	dest[index] = '\0';
	return index;
}

// sendCommand returns COMMAND_OK or COMMAND_ERROR
int sendCommand(const char* request, char* response) {
	char   line[LINE_BUFFER];
	size_t lineLen;

	if (response)
		response[0] = '\0';

	modemSerial.write(request);
	modemSerial.write("\r\n");
	modemSerial.flush();

	for (;;) {
		lineLen = modemReadline(line);
		if (String(line) == "OK") {
			return COMMAND_OK;
		} else if (String(line) == "ERROR") {
			return COMMAND_ERROR;
		} else if (response && line[0] != '\0') {
			if (response[0] != '\0')	// check if not empty string
				strcat(response, "\n");
			strcat(response, line);
		}
	}
	delay(100);	   // wait 1/10
}

int sendCommand(const char* request) {
	return sendCommand(request, NULL);
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


	usbSerial.print("[INFO] Waiting for module to response");
	for (;;) {
		usbSerial.print('.');
		modemSerial.write("AT\r\n");
		delay(100);
		if (modemSerial.available())
			break;
	}
	while (modemSerial.available())	   // clear cache
		modemSerial.read();
	usbSerial.println();

	sendCommand("ATE0");	// disable command-echo

	usbSerial.println("[INFO] Disabled command-echo");

	if (sendCommand("AT+CPIN=\"" SIM_PIN "\"") == COMMAND_ERROR) {
		usbSerial.println("[ERROR] SIM can't be unlocked, wrong PIN");
		return;
	}

	sendCommand("AT+CPSMS=0");	   // Disable Power Saving Mode
	sendCommand("AT+CEDRXS=0");	   // Disable eDRX

	sendCommand("AT+CFUN=15");								  // Reset the module
	sendCommand("AT+UMNOPROF=1");							  // Set MNO profile (1=automatic,100=standard europe)
	sendCommand("AT+URAT=7");								  // Set URAT to LTE-M
	sendCommand("AT+CEREG=3");								  // Enable URCs
	sendCommand("AT+CGDCONT=1,\"IP\",\"" APN_DOMAIN "\"");	  // Set the APN
	sendCommand("AT+COPS=0,2");								  // Autoselect the operator

	usbSerial.println("Waiting...");

	//	char response[100];
	//	while (sendCommand("AT+CSQ", response) == COMMAND_OK && strcmp(response, "+CSQ: 99,99"))
	//		;	 // Check Siganl strenght, repeat till you have a valid CSQ (99,99 means no signal)
	//	while (sendCommand("AT+CGATT?", response) == COMMAND_OK && !strcmp(response, "+CGATT: 1"))
	//		;	 // Check Siganl strenght, repeat till you have a valid CSQ (99,99 means no signal)

	usbSerial.println("Connected!");
}

void loop() {
	while (usbSerial.available())
		modemSerial.write(usbSerial.read());

	while (modemSerial.available())
		usbSerial.write(modemSerial.read());
}
