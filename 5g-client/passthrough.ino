#include "include/config.h"
#include "include/passthrough.h"

JSONVar readJSON() {
	char line[lineBuffer];
	char buf;
	int	 i = 0;
	for (;;) {
		while (!usbSerial.available())
			;
		buf = usbSerial.read();
		if (buf == '\r')
			continue;
		if (buf == '\n')
			break;
		line[i++] = buf;
	}
	line[i++] = '\0';

	return JSON.parse(line);
}

void passthrough::init() {
	usbSerial.println("{\"command\":\"hello\"}");
	JSONVar res_json = readJSON();
	if (res_json["error"] != nullptr) {
		// :(
	}
}

void passthrough::connect(const char* host, int port) {
	JSONVar body;
	body["command"] = "connect";
	body["host"]	= host;
	body["port"]	= port;

	usbSerial.println(body);
}

const char* passthrough::send(http_packet request, http_packet& response) {
	JSONVar body;
	body["command"]	 = "send";
	body["method"]	 = request.method;
	body["endpoint"] = request.endpoint;
	body["headers"]	 = request.headers;
	body["body"]	 = request.body;
	usbSerial.println(body);

	JSONVar res_json = readJSON();
	response.body	 = res_json["body"];
	response.headers = res_json["headers"];

	return res_json["error"];
}


const char* passthrough::send(http_packet request) {
	JSONVar body;
	body["command"]	 = "send";
	body["method"]	 = request.method;
	body["endpoint"] = request.endpoint;
	body["headers"]	 = request.headers;
	body["body"]	 = request.body;
	usbSerial.println(body);

	JSONVar res_json = readJSON();

	return res_json["error"];
}
