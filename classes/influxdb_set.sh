#!/bin/bash

response=$1
file1='/etc/influxdb/influxdb.conf'
oldline=$(grep -F query-log-enabled "${file1}")
newline='query-log-enabled = false'
newline2='# query-log-enabled = true'

#reduce logfile entries
if [[ "$response" =~ ^([yY][eE][sS]|[yY])+$ ]]; then
	if ! [ "$oldline" = "$newline" ]; then
		sudo sed -i "s/${oldline}/${newline}/g" "$file1"
	fi

	if ! [ "influx -execute 'SHOW DATABASES' | grep boatdata" = 'boatdata' ]; then
		curl -X POST http://localhost:8086/query?q=CREATE+DATABASE+boatdata
	fi

else
	if ! [ "$oldline" = "$newline2" ]; then
		sudo sed -i "s/${oldline}/${newline2}/g" "$file1"
	fi

	if ! [ "influx -execute 'SHOW DATABASES' | grep boatdata" = 'boatdata' ]; then
		curl -X POST http://localhost:8086/query?q=DROP+DATABASE+boatdata
	fi

fi
