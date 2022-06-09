#pragma once

enum command_status {
	COMMAND_OK		= 0,	// command succeed
	COMMAND_ERROR	= 1,	// command returned an error
	COMMAND_TIMEOUT = 2		// command timed out
};

enum command_flags {
	COMMAND_NONE,				// none of them underneath
	COMMAND_SILENT = 1 << 0,	// no debug messages (for looped commands)
	COMMAND_BLOCK  = 1 << 1,	// no time-out (for waiting commands)
	COMMAND_EVENT  = 1 << 2,	// handle '+'-responses as event
};

command_status sendCommand(const char* request, char* response, command_flags flags = COMMAND_NONE);
command_status sendCommand(const char* request, command_flags flags = COMMAND_NONE);