## This is the development branch of OpenPlotter project. If you want to test this version, you have to download the system image from:

http://www.sailoog.com/en/blog/download-openplotter-rpi-v090alpha-noobs

To apply updates and solved issues, delete the openplotter folder and download it again:

`cd`

`cd .config`

`rm -rf openplotter/`

`git clone -b v0.9.0 https://github.com/sailoog/openplotter.git`

`sudo chmod 775 /home/pi/.config/openplotter/openplotter`

`sudo chmod 775 /home/pi/.config/openplotter/keyword`

### Known issues

- [x] [SOLVED] SDR AIS decodification doesn't work if network connection is not present.
- [ ] Node-Red crashes after hours of function.

### To Do list

- [ ] Write a GUI for startup script to show startup process, inform of errors and show recommendations (changing pi user, access point and VNC passwords)
- [ ] Build a better default Node-RED flow to feed freeboard and Node-RED Dashboard
- [ ] Rebuild calculations.
- [ ] Rebuild the Actions system to implement the new signalk-server-node plugin to create alarm zones for signalk keys.
- [ ] Rebuild the MQTT system to perform the signalk specification.
- [ ] Set beginners/expert modes.
- [ ] Add local documentation (pdf).
- [ ] Set Android USB tethering for internet connection (and SMS?).
- [ ] Use gprx for better AIS reception?.
- [ ] Translations.

### We are updating documentation:

https://sailoog.gitbooks.io/openplotter-documentation/content/en/
