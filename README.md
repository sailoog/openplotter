## This is the development branch of OpenPlotter project. If you want to test this version, you have to follow these steps:

* Run OpenPlotter v0.8.0

* Delete the old content and clone this branch in folder /home/pi/.config/openplotter

* Type in the terminal:

`sudo chmod 775 /home/pi/.config/openplotter/openplotter`

`sudo chmod 775 /home/pi/.config/openplotter/keyword`

* Add to file /home/pi/.profile:

`export PATH=$PATH:/home/pi/.config/openplotter`

* Install isc-dhcp-server:

`sudo apt-get install isc-dhcp-server`

* Replace the content of file /home/pi/.config/signalk-server-node/settings/openplotter-settings.json by:

`{`
	`"vessel" : {`
		`"mmsi" : "000000000",`
		`"uuid" : "urn:mrn:imo:mmsi:000000000"`
	`},`
	`"pipedProviders" : [{`
			`"pipeElements" : [{`
					`"type" : "providers/tcp",`
					`"options" : {`
						`"host" : "127.0.0.1",`
						`"port" : "10110"`
					`}`
				`}, {`
					`"type" : "providers/nmea0183-signalk",`
					`"optionMappings" : [{`
							`"toOption" : "selfId",`
							`"fromAppProperty" : "selfId"`
						`}, {`
							`"toOption" : "selfType",`
							`"fromAppProperty" : "selfType"`
						`}`
					`]`
				`}`
			`],`
			`"id" : "kplexOutput"`
		`}, {`
			`"pipeElements" : [{`
					`"type" : "providers/udp",`
					`"options" : {`
						`"port" : "55556"`
					`}`
				`}, {`
					`"type" : "providers/liner"`
				`}, {`
					`"type" : "providers/from_json"`
				`}`
			`],`
			`"id" : "I2Csensors"`
		`}, {`
			`"pipeElements" : [{`
					`"type" : "providers/udp",`
					`"options" : {`
						`"port" : "55557"`
					`}`
				`}, {`
					`"type" : "providers/liner"`
				`}, {`
					`"type" : "providers/from_json"`
				`}`
			`],`
			`"id" : "1Wsensors"`
		`}, {`
			`"pipeElements" : [{`
					`"type" : "providers/udp",`
					`"options" : {`
						`"port" : "55558"`
					`}`
				`}, {`
					`"type" : "providers/liner"`
				`}, {`
					`"type" : "providers/from_json"`
				`}`
			`],`
			`"id" : "notifications"`
		`}, {`
			`"pipeElements" : [{`
					`"type" : "providers/execute",`
					`"options" : {`
						`"command" : "actisense-serial /dev/ttyOP_N2K"`
					`}`
				`}, {`
					`"type" : "providers/liner"`
				`}, {`
					`"type" : "providers/n2kAnalyzer"`
				`}, {`
					`"type" : "providers/n2k-signalk"`
				`}`
			`],`
			`"id" : "CAN-USB"`
		`}`
	`],`
	`"interfaces" : {}`
`}`

* Reset and open OpenPlotter typing:

`openplotter`
