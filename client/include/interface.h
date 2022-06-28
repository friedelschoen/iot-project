#pragma once

#include <Arduino_JSON.h>


typedef JSONVar json;

extern json null_response;

struct interface {
	enum method {
		METHOD_GET,
		METHOD_POST
	};

	enum command_status {
		STATUS_OK		 = 0,	 // command succeed
		STATUS_ERROR	 = 1,	 // command returned an error
		STATUS_TIMEOUT	 = 2,	 // command timed out
		STATUS_NOT_READY = 3,	 // interface is not ready
	};

	enum command_flags {
		COMMAND_NONE,				// none of them underneath
		COMMAND_FORCE  = 1 << 0,	// ignore modemReady/remoteReady
		COMMAND_BLOCK  = 1 << 1,	// no time-out (for waiting commands)
		COMMAND_IGNORE = 1 << 2,	// don't wait for response, just wait $ignoreDelay secounds
	};

  protected:
	bool remoteReady = false;
	bool modemReady	 = false;

	void beginModem();

	void beginRemote();
	void endRemote();

  public:
	char token[17];

	json request, response;

	void begin();

	int send(method method, const char* endpoint);

	command_status remote(const char* command, json params = nullptr, json& response = null_response, command_flags flags = COMMAND_NONE);

	command_status modem(const char* request, char* response, command_flags flags = COMMAND_NONE);
	command_status modem(const char* request, command_flags flags = COMMAND_NONE);
};