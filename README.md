# What is OpenPlotter?

![OpenPlotter RPI](https://sailoog.gitbooks.io/openplotter-documentation/content/en/openplotter.png)

There are people who buy boats but there are also people who build them, why not build your own electronics too? OpenPlotter is a combination of software and hardware to be used as navigational aid on small and medium boats. It is also a complete home automation system onboard. It works on ARM computers like the [Raspberry Pi](https://www.raspberrypi.org/) and is open-source, low-cost and low-consumption. Its design is modular, so you just have to implement what your boat needs. Do it yourself.

## Features

* **Chartplotter**. With [OpenCPN](http://opencpn.org), a navigation software with useful plugins.
* **Weather Forecast**. Download and visualize GRIB files with [zyGrib](http://www.zygrib.org).
* **NMEA 0183 Multiplexer**. Multiplex and filter data inputs from any number of serial and network interfaces. Send and filter to any number of outputs.
* **Signal K (beta)**. OpenPlotter is ready for [Signal K](http://signalk.org/), the new, free and open source universal marine data exchange.
* **Inspector**. Check the data traffic to avoid conflicts and overlaps between sources.
* **WiFi Access Point**. Share data (NMEA 0183, Signal K, remote desktop, Internet connection) with laptops, tablets and phones onboard. Connect to internet on port through the same device.
* **Remote Desktop**. Access to OpenPlotter desktop from the cockpit through your mobile devices.
* **Headless**. Easy start without monitor.
* **SDR-AIS**. Receive and decode AIS with cheap DVB-T dongles. Calibration tools Included.
* **Electronic Compass and Heel**. Read magnetic heading and heel angle from an IMU sensor. Tilt compensated. Calibration tools Included.
* **Barograph, Thermograph and Hygrograph**. From pressure, temperature and humidity sensors. Save logs and display graphs to see trends.
* **Multiple temperature sensors**. Get data from coolant engine, exhaust, fridge, sea...
* **Special Sensors**. Detect opening doors/windows, tanks level, human body motion...
* **Magnetic Variation**. Calculate magnetic variation for date and position.
* **True Heading**. Calculate true heading from magnetic variation and magnetic heading.
* **True Wind**. Calculate true wind from apparent wind and either speed through water (speed log) or speed over ground (GPS).
* **Rate Of Turn**. Calculate the rate the ship is turning.
* **Remote Monitoring**. Publish data on Twitter or send it by email.
* **Actions System**. Compare a custom value with any data flowing through your system and use it as a trigger to run multiple predefined actions.
* **Custom Switches**. Connect external switches and link them with actions.
* **Handle External Devices**. Relays, LEDs, buzzers ...
* **System Time Tools**. Set the system time from NMEA data and set the time zone easily.
* **Startup Programs**. Select some program parameters to automatically launch at start.

## Project site

http://www.sailoog.com/openplotter


## Build instructions

https://github.com/sailoog/openplotter/wiki


![OpenPlotter RPI](https://sailoog.gitbooks.io/openplotter-documentation/content/en/openplotter_rpi.png)
