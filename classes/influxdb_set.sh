#!/bin/bash

response=$1
duration=$2
file1='/etc/influxdb/influxdb.conf'
oldline=$(grep -F query-log-enabled "${file1}")
newline='query-log-enabled = false'
newline2='# query-log-enabled = true'
dbexist=$(influx -execute 'SHOW DATABASES' | grep boatdata)

#reduce logfile entries
if [[ "$response" =~ ^([yY][eE][sS]|[yY])+$ ]]; then
	if ! [ "$oldline" = "$newline" ]; then
		sudo sed -i "s/${oldline}/${newline}/g" "$file1"
	fi
	if [ "$dbexist" == "boatdata" ]; then
		curl -X POST http://localhost:8086/query?q=ALTER+RETENTION+POLICY+boatdatapolicy+ON+boatdata+DURATION+$duration+REPLICATION+1+DEFAULT
	else
		curl -X POST http://localhost:8086/query?q=CREATE+DATABASE+boatdata
		curl -X POST http://localhost:8086/query?q=CREATE+RETENTION+POLICY+boatdatapolicy+ON+boatdata+DURATION+$duration+REPLICATION+1+DEFAULT
	fi
else
	if ! [ "$oldline" = "$newline2" ]; then
		sudo sed -i "s/${oldline}/${newline2}/g" "$file1"
	fi
	if [ "$dbexist" == "boatdata" ]; then
		curl -X POST http://localhost:8086/query?q=DROP+DATABASE+boatdata
		curl -X POST http://localhost:8086/query?q=DROP+RETENTION+POLICY+boatdatapolicy+ON+boatdata
	fi
fi
