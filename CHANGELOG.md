v0.14.1
* Remove deviation table from Compass tab

v0.14.0
* New IMU management, add Compass tab

v0.13.1
* Remove real VNC server and reinstall xrdp

v0.13.0
* Update dependencies
* Update Raspbian packages
* Switch source code to openplotter organization repository
* Restore SK keys when editing
* Add pop up when 1W is disabled
* Add deg, knots, °C, F conversion on NMEA 0183 generator
* Add default SK keys to I2C sensors
* Add deviation table
* Add deviation table to true heading calculation

v0.12.0
* Update dependencies
* Update Raspbian packages
* Switch to repository Nick-Currawong/RTIMULib2
* Add IMU InvenSense MPU-9255
* Fix IMU calibration buttons
* Add Heading True calculation
* Add Rate of Turn calculation

v0.11.11
* Remove unused packages when updating
* Keep imu calibration data after updating

v0.11.10
* Add tool for INA21
* Add USB tethering Android fixed IP
* Update language sources
* Fix hotspot
* Add show calibration comparation tool
* Fix magnetic variation calculation

v0.11.9
* Fix I2C sensors detection
* Fix IMU ellipsoid calibration

v0.11.8
* I2C sensors detection workaround
* Cosmetic changes
* fix N2K output on startup issue

v0.11.7
* Add Set Signal K key value action
* Improve error messages in actions
* Add check I2C addresses button
* Fix add MQTT interface error

v0.11.6
* Fix general MQTT topics actions
* Fix SPI

v0.11.5
* Fix GPIO output actions
* WIFI AP interface improvement

v0.11.4
* New interface for I2C
* Fix I2C
* Add support for BME280 sensors (press, temp, hum)

v0.11.3
* New interface for actions. Parsing signal k values on actions data.
* Fix Twwitter and Gmail actions
* Fix SMS actions
* Fix sounds actions
* Fix messages actions
* Fix wait, reset, shutdown, startup stop, startup restart actions
* Rename signal k settings labels
* optimize signal k restart

v0.11.2
* Fix 1W
* Fix NMEA 0183 generator
* Fix ADS1115
* Fix Actions. Some actions need still to be revised but triggers are working right. Stop and start all actions needs revision too

v0.11.1
* Add openplotter debugging to menu. To see the neu item go to: Updates - Set default openplotter desktop
* Fix bug in CHANGELOG file

v0.11.0
* New interface for triggers (actions not working properly yet)
* Fixing bug with NMEA 2000 sources
* Optimizing Signal k diagnostic
* Fixing bug with kplex
* Optimizing startup
* Adding up to 4 ADS1115
* Update Signal k node server

v0.10.2
* updating new signal k settings file with old signal k settings

v0.10.1
* Liner providers deleted from UDP inputs in Signal K settings
* Deleted unused serial input from Signal K settings
* Deleted default N2K input from Signal K settings
* Added this changelog file
* Fixed sources in SK diagnostic window
* Fixed sources in SK-base daemon

