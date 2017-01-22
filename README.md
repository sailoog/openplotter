## This is the development branch of OpenPlotter project. If you want to test this version, you have to download the system image from:

http://www.sailoog.com/en/blog/download-openplotter-rpi-v090alpha-noobs

To apply updates/install and solved issues, start:

'bash update_OP.sh'

(If the file isn't in the home directory you can find it here: https://github.com/sailoog/openplotter/blob/v0.9.0/OP-signalk/update_OP.sh )

### Known issues

- [x] [SOLVED] SDR AIS decodification doesn't work if network connection is not present.
- [ ] Node-Red crashes after hours of function.

### To Do list

- [x] [DONE] Write a GUI for startup script to show startup process, inform of errors and show recommendations (changing pi user, access point and VNC passwords)
- [x] [DONE] startup can be started from terminal `startup stop` + `startup` is the same as `startup restart` (for debug, warm restart and stop OpenPlotter server processes)
- [ ] Build a better default Node-RED flow to feed freeboard and Node-RED Dashboard
- [ ] Rebuild calculations.
- [ ] Rebuild the Actions system to implement the new signalk-server-node plugin to create alarm zones for signalk keys.
- [ ] Rebuild the MQTT system to perform the signalk specification.
- [ ] Set beginners/expert modes.
- [x] Add local documentation (pdf).
- [ ] Set Android USB tethering for internet connection (and SMS?).
- [ ] Use gprx for better AIS reception?.
- [ ] Translations.
- [x] SignalK can be installed/updated without adding any OpenPlotter setting files
- [x] OpenPlotter SPI can be completly disabled (issues with some touch screen drivers)

### We are updating documentation:

https://sailoog.gitbooks.io/openplotter-documentation/content/en/
