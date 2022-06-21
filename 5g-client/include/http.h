#pragma once

#include <Arduino_JSON.h>


typedef JSONVar json;

extern json null_response;

struct http_client {
	enum method {
		HTTP_GET,
		HTTP_POST
	};

  protected:
	bool remote = false;

	void fallback();

  public:
	bool ready = false;

	void begin();

	int send(method method, const char* endpoint, const char* body = "{}", json& response = null_response);
	int send(method method, const char* endpoint, json body = nullptr, json& response = null_response);
};