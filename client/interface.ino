#include "include/config.h"
#include "include/interface.h"
#include "include/led.h"

json null_response;

static const char* method_strings[] = {
	[interface::METHOD_GET]	 = "GET",
	[interface::METHOD_POST] = "POST",
};

void interface::begin() {
	writeLED(COLOR_MAGENTA);

	usbSerial.begin(remoteBaud);
	usbSerial.setTimeout(remoteTimeout);

	if (remoteForce)
		return;

	pinMode(modemPowerPin, OUTPUT);		 // Put voltage on the nb-iot module
	pinMode(modemVoltagePin, OUTPUT);	 // Switch module voltage
	pinMode(modemEnablePin, OUTPUT);	 // Set state to active

	digitalWrite(modemPowerPin, HIGH);
	digitalWrite(modemVoltagePin, LOW);
	digitalWrite(modemEnablePin, HIGH);
	modemSerial.begin(modemBaud);

	while (!modemSerial)
		;

	// -*- module initialization -*-
	for (;;) {
		modemSerial.write("AT\r\n");
		delay(1000);
		if (modemSerial.available())
			break;
	}

	while (modemSerial.available())	   // clear cache
		modemSerial.read();

	// commands...

	modemReady = true;

	writeLED(COLOR_BLUE);
}

void interface::beginRemote() {
	if (remoteReady)	// already initalizised
		return;

	writeLED(COLOR_RED);
	while (!usbSerial)
		;
	writeLED(COLOR_YELLOW);

	remoteReady = true;
}

void interface::endRemote() {
	if (!remoteReady)
		return;

	writeLED(COLOR_BLUE);

	json response;
	remote("hello", nullptr, response, COMMAND_FORCE);
	const char* debug = response["debugToken"];
	memcpy(debugToken, debug, sizeof(debugToken));

	remoteReady = false;
}

int interface::send(interface::method method, const char* endpoint, json body, json& response) {
	int code;

	if (usbSerial || !modemReady) {
		beginRemote();

		json request;

		body["debugToken"] = debugToken;

		request["method"]	= method_strings[method];
		request["endpoint"] = endpoint;
		request["body"]		= body;

		json cmd_response;
		if (remote("send", request, cmd_response))
			return 0;

		response = cmd_response["body"];
		return cmd_response["code"];
	} else {
		endRemote();
		// modem
	}
	return code;
}

interface::command_status interface::remote(const char* command, json params, json& response, command_flags flags) {
	bool force = flags & COMMAND_FORCE;

	if (!force && !remoteReady)
		return interface::STATUS_NOT_READY;

	usbSerial.print(command);
	usbSerial.print(" ");
	params.printTo(usbSerial);
	usbSerial.print("\n");

	String status = usbSerial.readStringUntil(' ');
	if (!status.length()) {
		return interface::STATUS_TIMEOUT;
	} else if (status == "ok") {
		response = json::parse(usbSerial.readStringUntil('\n'));
		return interface::STATUS_OK;
	} else {
		response = status;
		return interface::STATUS_ERROR;
	}
}

interface::command_status interface::modem(const char* request, char* response, command_flags flags) {
	char   line[lineBuffer];
	size_t lineLen;
	char   buf;

	bool force	= flags & COMMAND_FORCE,
		 block	= flags & COMMAND_BLOCK,
		 ignore = flags & COMMAND_IGNORE;

	if (!force && !modemReady)
		return interface::STATUS_NOT_READY;

	if (response)
		response[0] = '\0';

	modemSerial.write("AT");
	modemSerial.write(request);
	modemSerial.write("\r\n");


	delay(commandDelay * 1000);
}

interface::command_status interface::modem(const char* request, command_flags flags) {
	return modem(request, NULL, flags);
}
