## This is the development branch of OpenPlotter project. If you want to test this version, you have to follow these steps:

* Run OpenPlotter v0.8.0

* Delete the old content and clone this branch in folder /home/pi/.config/openplotter

* Type in the terminal:

`sudo apt-get update`

`sudo apt-get upgrade`

`sudo chmod 775 /home/pi/.config/openplotter/openplotter`

`sudo chmod 775 /home/pi/.config/openplotter/keyword`

* Add to file /home/pi/.profile:

`export PATH=$PATH:/home/pi/.config/openplotter`

* Install isc-dhcp-server:

`sudo apt-get install isc-dhcp-server`

* Install websocket-client python package:

`sudo pip install websocket-client`

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


* Reset and open OpenPlotter typing:

`openplotter`

In opencpn options connections change 10110 to 10109

if you want to use the analog tools for firmata and ads1115, then read tools/install analog.txt

changes:
-action on SignalK
-analog input MCP3008
-SignalK emulator
-generating nmea0183 sentences from SignalK
	can be tested with command `nc -ul 127.0.0.1 55565`
-generating nmea2000 sentences from SignalK
	not implemented in the ide, so you have to choose the pgn in openplotter.conf [N2K] pgn_generate =['127489']
-many pages are resizeable
