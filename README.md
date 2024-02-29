# WP4_Inorganic_Synthesis_Platform
A complete set of integrated scripts enabling automation of all process steps in the inorganic sol gel syntheis to produce Al2O3 coatings on NMC electrode powders.

The current version of the software has been designed and tested for a an inorganic sol-gel synthesis protocol for the coating of NMC622 (LiNi0.6Mn0.2Co0.2O2) electrode powders.

The inorganic synthesis route for the formation of coatings on nickel-rich layered oxide materials, for Li-ion positive electrodes, utilises a “Sol-Gel” synthetic procedure. The procedure targets alumina, Al2O3, as the desired benchmarking coating material and has been demonstrated using LiNi0.6Min0.2Co0.2O2 (code NMC622). The process for the sol-gel synthesis of Al2O3 coatings within an individual reaction vial is described in 5 primary steps: solid powder dosing, liquid component dosing (including Al-precursor solutions), reaction heating/mixing, solvent evaporation/removal, and calcination. 

The solid NMC622 powder (1 g) is dispensed into a glass vial. The bulk solvent (e.g., anhydrous 2-propanol) is first deposited into the glass vials (volume 40 mL), followed by the chelating agent and then the solvent solution containing the aluminium precursor (e.g., aluminium tri-sec-butoxide). The total liquid volume is fixed to 10 mL by adjusting the solvent volume. The resulting solid/liquid mixture is then heated with mixing for a given time before dry N2 is flowed into the vial to promote evaporation of the bulk solvent. The reaction mixture is then calcined in a natural convection furnace (400-675 °C). Integrating these steps into the described partially automated procedure completed in batches of 11 samples per rack, increases throughput to complete 22-44 samples per 6-7 h versus 6-7 h for 1 sample by a manual process. This increases the accessibility of the matrix of reaction variables/parameters that may be explored to optimize the coating conditions.

# Installation - Python Modules

1.	Download all repository files from GitHub
2.	Save all files into a new folder
3.	Install python 3 if you don’t already have it available (the platform was developed using winpython, so this may be simplest to use)
4.	Navigate to the python ‘scripts’ folder (example: C:\Program Files\WPy64-31090\scripts)
5.	Open the windows command prompt by, for instance, typing ‘cmd’ into the file path in windows explorer
6.	The scripts require several additional modules on top of those provided by winpython, these are shown below:
a.	PySimpleGUI
b.	requests
c.	pyautogui
d.	pyModbusTCP
7.	In the windows command prompt, install these modules using ‘pip install’ command, followed by the name of the module for example:
‘pip install PySimpleGUI’
8.	If, while running any of the scripts, an error appears saying they are missing a module, check the module name in the error message and install it with ‘pip install’ in the same location, eventually all necessary modules will be installed this way
9.	If modules still seem to be missing, make use of the ‘requirements.txt’ file in the same folder as the scripts. Move this file to the ‘scripts’ folder, and using the command prompt in this location, use the command: ‘pip install -r requirements.txt’ – this should install all the modules needed for the synthesis platform (and some that are not needed, hence it is better to install modules individually)
10.	Once the modules have been installed, it should be possible to run the relevant scripts form any PC

# Installation - Arduino Sketches

1.	Install Arduino IDE on any PC: https://support.arduino.cc/hc/en-us/articles/360019833020-Download-and-install-Arduino-IDE
2.	Connect the Arduino UNO microcontroller you intend to use to the PC with a USB cable
3.	In Arduino IDE, open the sketch ‘Sol-gel-reaction-microcontroller-sketch.ino’
4.	Install the necessary libraries using ‘library manager’ on the right hand side of the window, these are the following, which can be found using the search bar:
a.	Ethernet
b.	Arduino_MKRTHERM
c.	Adafruit BusIO
d.	Adafruit MAX31855
5.	Similar to python modules, if you attempt to load a sketch and a module is missing, this should be shown in the error message and you can install the relevant library
6.	Select the Arduino board from the ‘select board’ menu
7.	Click ‘Upload’ – once this has concluded, the UNO microcontroller will runs the sketch on a loop so long as it is powered on
8.	Repeat these steps for the Arduino MKR board you plan to use, also by connecting it to your PC with a USB cable and installing the sketch ‘thermocouple-microcontroller-sketch.ino’
