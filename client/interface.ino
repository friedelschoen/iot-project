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

	delay(2500);

	sendToken();

	writeLED(COLOR_MAGENTA);
	remoteReady = true;
}

void interface::endRemote() {
	if (!remoteReady)
		return;

	writeLED(COLOR_BLUE);
	remoteReady = false;
}

int interface::send(interface::method method, const char* endpoint) {
	if (usbSerial) {
		beginRemote();

		json cmd_request;
		cmd_request["method"]	= method_strings[method];
		cmd_request["endpoint"] = endpoint;
		cmd_request["body"]		= request;

		json cmd_response;
		if (remote("send", cmd_request, cmd_response))
			return 0;

		request	 = nullptr;
		response = cmd_response["body"];
		return cmd_response["code"];
	} else if (modemReady) {
		endRemote();
		// modem
		return 0;
	} else {
		endRemote();
		writeLED(COLOR_RED);
		return 0;
	}
}

void interface::sendToken() {
	json req;
	req["token"] = config.token;
	remote("set_token", req, null_response, COMMAND_FORCE);
}


interface::command_status interface::remote(const char* command, json params, json& response, command_flags flags) {
	bool force = flags & COMMAND_FORCE;

	if (!force && !remoteReady)
		return interface::STATUS_NOT_READY;

	usbSerial.print(command);
	usbSerial.print(" ");
	params.printTo(usbSerial);
	usbSerial.print("\n");

	String line = usbSerial.readStringUntil('\n');
	String status;
	if (line.indexOf(' ') != -1) {
		status	 = line.substring(0, line.indexOf(' '));
		response = json::parse(line.substring(line.indexOf(' ') + 1));
	} else {
		status = line;
	}
	if (!status.length()) {
		return interface::STATUS_TIMEOUT;
	} else if (status == "ok") {
		return interface::STATUS_OK;
	} else {
		response = status;
		return interface::STATUS_ERROR;
	}
}

interface::command_status interface::modem(const char* request, char* response, command_flags flags) {
	return STATUS_NOT_READY;
	/*
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


	delay(commandDelay * 1000);*/
}

interface::command_status interface::modem(const char* request, command_flags flags) {
	return modem(request, NULL, flags);
}
