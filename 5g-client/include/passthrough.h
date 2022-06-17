#pragma once

#include <Arduino_JSON.h>

struct passthrough {
	struct http_packet {
		const char* method;
		const char* endpoint;
		JSONVar		headers;
		JSONVar		body;
	};

	void		init();
	void		connect(const char* host, int port);
	const char* send(http_packet request, http_packet& response);
	const char* send(http_packet request);
};