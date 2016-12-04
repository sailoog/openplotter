## This is the development branch of OpenPlotter project. If you want to test this version, you have to download the system image from:

http://www.sailoog.com/en/blog/download-openplotter-rpi-v090alpha-noobs

We are updating documentation:

https://sailoog.gitbooks.io/openplotter-documentation/content/en/

### Known issues

- [ ] SDR AIS decodification doesn't work if network connection is not present. Possible cause: https://www.reddit.com/r/RTLSDR/comments/4yu0a6/rtl_ais_error_on_raspberry_pi/

### To Do list

- [ ] Write a GUI for startup script to show startup process, inform of errors and show recommendations (changing pi user, access point and VNC passwords)
- [ ] Build a better default Node-RED flow to feed freeboard and Node-RED Dashboard
- [ ] Rebuild the Actions system to implement the new signalk-server-node plugin to create alarm zones for signalk keys.
- [ ] Rebuild the MQTT system to perform the signalk specification.
- [ ] Translations




