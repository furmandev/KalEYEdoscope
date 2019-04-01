Setup:

In a command prompt, run "python setup.py install"

Arguments:
    -d: Display on default screen (not OLED screen)
    -k: Accept input using up, down, and q keys (only compatible when used with -d command)
    -c: Accept input from the command line

Dependencies list:
	* math
	* random
	* sys
	* matplotlib
	* numpy
	* yaml
	* pylab
	* scipy
Dependecies for OLED display
	* RPi.GPIO
	* OLED_Driver (included in this repo)
	* PIL (pillow)
Dependencies for regular display: 
	* pygame
	* os
	* operator
