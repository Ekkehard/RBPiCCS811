CCS811 Indoor Air Quality Sensor Driver for Raspberry Pi
========================================================

This software was designed as a Python module driver for the Cambridge CMOS 
Sensors' Ultra-Low Power Digital Gas Sensor for Monitoring Indoor Air Quality
CCS811.  This sensor is capable of measuring CO<sub>2</sub> content in Parts 
Per Million (ppm) and the concentration of total Volatile Organic Compounds 
(tVOC) in Parts Per Billion (ppb).  The sensor can operate in poll mode, 
where the calling software must always check whether new data is available 
before reading it or in interrupt mode, where the calling program is free to 
perform other tasks while the driver is interrupted by the sensor whenever 
new data has become available and then handles the acquisition of that data 
completely transparently.  To conserve battery power, the sensor also allows 
to be sent to sleep mode where it consumes very little power and then be 
woken up again to make some measurements.  Moreover, the sensor accepts the 
input of temperature and humidity measurements which the sensor does not 
measure internally but can use to provide more accurate CO<sub>2</sub> and tVOC 
measurements.

This software is intended to run on any model of the Raspberry Pi, including the
Raspberry Pi Pico, and supports all of the above mentioned operational modes on 
all these Raspberry Pi architectures.  To seamlessly span all different 
Raspberry Pi architectures, this software uses the Python GPIO Abstraction layer 
module GPIO_AL by the same author, which will therefore also need to be 
installed and is available here: https://github.com/Ekkehard/RBPiGPIO_AL.

Please note that a new sensor requires a 48 hour burn in.  Once burned in, a 
sensor requires to run for 20 minutes before readings are stable and considered 
valid.

For a complete documentation of this Python module, please see the docs 
directory https://ekkehard.github.io/RBPiCCS811/

Version History
---------------
* [1.0.0] -- Initial commit (outside of github)
* [1.1.0] -- Now uses GPIO_AL for better separation of architecture-specific 
             details from the general functionality of the code

License Information
-------------------
This code is _**Free and Open Source Software**_! 

Please see the LICENSEe.md and COPYING.md files for more detailed license 
information.  