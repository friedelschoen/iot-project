#pragma once

#define modemSerial		Serial1
#define modemPowerPin	SARA_ENABLE
#define modemEnablePin	SARA_TX_ENABLE
#define modemVoltagePin SARA_R4XX_TOGGLE


struct sara_modem {
	// -*- enums and structs -*-
	enum command_status {
		COMMAND_OK		= 0,	// command succeed
		COMMAND_ERROR	= 1,	// command returned an error
		COMMAND_TIMEOUT = 2		// command timed out
	};

	enum command_flags {
		COMMAND_NONE,				// none of them underneath
		COMMAND_SILENT = 1 << 0,	// no debug messages (for looped commands)
		COMMAND_BLOCK  = 1 << 1,	// no time-out (for waiting commands)
		COMMAND_IGNORE = 1 << 2,	// don't wait for response, just wait $ignoreDelay secounds
		COMMAND_EVENT  = 1 << 3,	// handle '+'-responses as event
	};

	// -*- declarations -*-
	void		   init();
	command_status send(const char* request, char* response, command_flags flags = COMMAND_NONE);
	command_status send(const char* request, command_flags flags = COMMAND_NONE);
};
