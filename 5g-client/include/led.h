#pragma once


struct status_led {
	enum color {
		COLOR_NONE,
		COLOR_RED,
		COLOR_GREEN,
		COLOR_BLUE,
		COLOR_YELLOW,
		COLOR_CYAN,
		COLOR_MAGENTA,
		COLOR_WHITE,
	};

  protected:
	color color0 = COLOR_NONE, color1 = COLOR_NONE;

  public:
	void begin();
	void set(color c);
	void set(color c0, color c1);
	void blink();
};

extern status_led led;