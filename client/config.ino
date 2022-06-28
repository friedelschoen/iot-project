#include "include/config.h"

FlashStorage(config_flash, configuration);

configuration config_default{
	true,	 // valid
	"",		 // token
	"",		 // domain,
};

configuration config;

void configuration::open() {
	*this = config_flash.read();
}

void configuration::save() {
	config_flash.write(*this);
}