Influxdb + Grafana
##################

.. image:: img/grafana.png

How to activate data logging with signalk influxdb grafana

OpenPlotter

1. Create database "boatdata"

Signal K

1. call openplotter.local:3000 in a browser
2. login signalk
3. Server Plugin Config InfluxDb writer
4. Check InfluDB writer Active
5. Enter for example environment.outside.pressure in the field under "Path*"
   (Enter more path if you wish or don't enter any path and switch Type of List to Black)
6. Submit

Grafana

1. call openplotter.local:3001 in a browser
2. login as user admin password admin and enter new password
3. choose datasource InfluxDB
4. settings 

	URL: http://openplotter.local:8086

	Database: boatdata
	
5. Button Save & Test (there should be a green band Data source is working)
6. Click the "+" symbol on the menu on the left side  Create Dashboard
7. Add Query
8. In line FROM click on select measurement (there should be a list of saved signalk path)
9. Click on the clock symbol top right menu and select last 5 minutes (now you should see a graf)
10. Click on save symbol

Now play with grafana.
