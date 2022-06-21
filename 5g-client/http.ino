#include "include/config.h"
#include "include/http.h"
#include "include/led.h"

json null_response;

void http_client::begin() {
	led.set(status_led::COLOR_NONE, status_led::COLOR_CYAN);

	if (remoteForce) {
		fallback();
		return;
	}
}

void http_client::fallback() {
	led.set(status_led::COLOR_RED, status_led::COLOR_YELLOW);
	remote = true;

	usbSerial.begin(remoteBaud);
	while (!usbSerial)
		led.blink();

	led.set(status_led::COLOR_YELLOW);
}

int http_client::send(http_client::method method, const char* endpoint, json body, json& response) {
	static char buffer[512];
	json::stringify(body).toCharArray(buffer, 512);
	return send(method, endpoint, buffer, response);
}

int http_client::send(http_client::method method, const char* endpoint, const char* body, json& response) {
	int code;
	if (!remote) {

	} else {
		switch (method) {
			case http_client::HTTP_GET:
				usbSerial.print("GET ");
				break;
			case http_client::HTTP_POST:
				usbSerial.print("POST ");
		}
		usbSerial.print(endpoint);
		usbSerial.print(" ");
		usbSerial.println(body);
		//		body.printTo(usbSerial);
		usbSerial.println();

		char buffer[256];
		int	 i	   = 0;
		int	 state = 0;	   // 0 = status-code; 1 = json
		char c;

		for (;;) {
			if (usbSerial.available()) {
				c = usbSerial.read();
				if (c == '\r') {
					// do nothing
				} else if (state == 0 && c == ' ') {
					buffer[i++] = '\0';
					code		= atoi(buffer);
					i			= 0;
					state		= 1;
				} else if (state == 1 && c == '\n') {
					buffer[i++] = '\0';
					response	= json::parse(buffer);
					break;
				} else {
					buffer[i++] = c;
				}
			}

			led.blink();
		}
	}
	return code;
}