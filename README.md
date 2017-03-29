## This is the development branch of OpenPlotter project. We will release a new version soon.


### Known issues

...

### To Do list

- [x] Next image will be self-updating. Minor changes (OP code), major changes (OP code + dependencies) and upgrades (minor, major and Raspbian upgrades).
- [x] Write a GUI for startup script to show startup process, inform of errors and show recommendations (changing pi user, access point and VNC passwords)
- [x] startup can be started from terminal `startup stop` + `startup` is the same as `startup restart` (for debug, warm restart and stop OpenPlotter server processes)
- [ ] Build a better default Node-RED flow to feed freeboard and Node-RED Dashboard
- [ ] Rebuild calculations.
- [ ] Rebuild the Actions system to implement the new signalk-server-node plugin to create alarm zones for signalk keys.
- [x] Rebuild the MQTT system to perform the signalk specification.
- [x] Rebuild GPIO system.
- [ ] Set beginners/expert modes.
- [x] Add local documentation (pdf).
- [ ] Set Android USB tethering for internet connection (and SMS?).
- [ ] Use gprx for better AIS reception?.
- [ ] Translations.
- [x] SignalK can be installed/updated without adding any OpenPlotter setting files
- [x] OpenPlotter SPI can be completly disabled (issues with some touch screen drivers)

### We are updating documentation:

https://sailoog.gitbooks.io/openplotter-documentation/content/en/
