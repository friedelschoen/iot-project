#include "include/config.h"

FlashStorage(config_flash, configuration);

configuration default_config{
	/*.valid	   =*/true,
	/*.simPIN	   =*/"",
	/*.simPUK	   =*/"",
	/*.simAPN	   =*/"",
	/*.domain	   =*/"muizenval.tk",
	/*.userToken =*/""
};

configuration config_current;