## This is the development branch of OpenPlotter project. If you want to test this version, you have to follow these steps:

* Run OpenPlotter RPI v0.8.0

* Delete OpenPlotter v0.8.0 scripts and clone v0.9.0 branch:

`cd /home/pi/.config`

`rm -rf openplotter/`

`git clone -b v0.9.0 https://github.com/sailoog/openplotter.git`

* Type in the terminal:

`sudo apt-get update`

`sudo apt-get upgrade`

`sudo chmod 775 /home/pi/.config/openplotter/openplotter`

`sudo chmod 775 /home/pi/.config/openplotter/keyword`

* Add to file /home/pi/.profile:

`export PATH=$PATH:/home/pi/.config/openplotter`

* Install isc-dhcp-server:

`sudo apt-get install isc-dhcp-server`

* Install python packages:

`sudo pip install websocket-client spidev`

* Replace the content of file /home/pi/.config/signalk-server-node/settings/openplotter-settings.json by:

{
	"vessel" : {
		"mmsi" : "00000000",
		"uuid" : "urn:mrn:imo:mmsi:00000000"
	},
	"pipedProviders" : [{
			"pipeElements" : [{
					"type" : "providers/udp",
					"options" : {
						"port" : "55556"
					}
				}, {
					"optionMappings" : [{
							"toOption" : "selfId",
							"fromAppProperty" : "selfId"
						}, {
							"toOption" : "selfType",
							"fromAppProperty" : "selfType"
						}
					],
					"type" : "providers/nmea0183-signalk"
				}
			],
			"id" : "kplexOutput"
		}, {
			"pipeElements" : [{
					"type" : "providers/udp",
					"options" : {
						"port" : "55557"
					}
				}, {
					"type" : "providers/liner"
				}, {
					"type" : "providers/from_json"
				}
			],
			"id" : "OP_sensors"
		}, {
			"pipeElements" : [{
					"type" : "providers/udp",
					"options" : {
						"port" : "55558"
					}
				}, {
					"type" : "providers/liner"
				}, {
					"type" : "providers/from_json"
				}
			],
			"id" : "notifications"
		}, {
			"pipeElements" : [{
					"type" : "providers/udp",
					"options" : {
						"port" : "55559"
					}
				}, {
					"type" : "providers/liner"
				}, {
					"type" : "providers/from_json"
				}
			],
			"id" : "serial"
		}, {
			"pipeElements" : [{
					"type" : "providers/udp",
					"options" : {
						"port" : "55561"
					}
				}, {
					"type" : "providers/liner"
				}, {
					"type" : "providers/from_json"
				}
			],
			"id" : "wifi"
		}, {
			"pipeElements" : [{
					"type" : "providers/execute",
					"options" : {
						"command" : "actisense-serial /dev/ttyOP_N2K"
					}
				}, {
					"type" : "providers/liner"
				}, {
					"type" : "providers/n2kAnalyzer"
				}, {
					"type" : "providers/n2k-signalk"
				}
			],
			"id" : "CAN-USB"
		}
	],
	"interfaces" : {}
}

* Delete file /home/pi/.kplex.conf

* Reset and open OpenPlotter typing:

`openplotter`

* In opencpn Options>Connections, replace:

`localhost:10110 TCP input`

by

`localhost:10109 TCP input`

## Notes

if you want to use the analog tools for firmata and ads1115, then read tools/install analog.txt

changes:

-action on SignalK

-analog input MCP3008

-SignalK emulator

-generating nmea0183 sentences from SignalK can be tested with command `nc -ul 127.0.0.1 10110`

-generating nmea2000 sentences from SignalK not implemented in the ide, so you have to choose the pgn in openplotter.conf [N2K] pgn_generate =['127489']

-many pages are resizeable

