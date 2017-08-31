#!/usr/bin/env python
# This file is part of Openplotter.
# Copyright (C) 2017 by sailoog <https://github.com/sailoog/openplotter>
#
# Openplotter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
# Openplotter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Openplotter. If not, see <http://www.gnu.org/licenses/>.

import os
import time
import urllib2
import schedule  # This needs to be installed i.e. 'pip install schedule'
from datetime import datetime, timedelta

from classes.paths import Paths
from classes.conf import Conf


def run_scheduled():
    try:
        run()
    except Exception:
        print "Scheduled run failed"
    finally:
        print 'Next download is scheduled at ' + str(schedule.next_run())


def run():
    if clean == '1':
        clean_folder()

    download_grib()


def download_grib():
    utc_now = datetime.utcnow()
    now = datetime.now()

    # open configuration settings
    download_gust = conf.get('GRIB', 'download_gust')
    download_tmp = conf.get('GRIB', 'download_tmp')
    download_humidity = conf.get('GRIB', 'download_humidity')
    download_precipitation = conf.get('GRIB', 'download_precipitation')
    download_cape = conf.get('GRIB', 'download_cape')
    download_pressure = conf.get('GRIB', 'download_pressure')
    download_min_max_temp = conf.get('GRIB', 'download_min_max_temp')
    download_wind = conf.get('GRIB', 'download_wind')
    download_cloud_cover = conf.get('GRIB', 'download_cloud_cover')

    lon_min = float(conf.get('GRIB', 'lon_min'))
    lon_max = float(conf.get('GRIB', 'lon_max'))
    lat_min = float(conf.get('GRIB', 'lat_min'))
    lat_max = float(conf.get('GRIB', 'lat_max'))

    days = int(conf.get('GRIB', 'days'))
    source_file_count = days * 24  # Grib files are hourly based (until 12 days)

    # Validate configuration parameters
    if lon_min < -180 or lon_min > 180:
        raise ValueError('longitude should be between -180 and 180')

    if lon_max < -180 or lon_max > 180:
        raise ValueError('longitude should be between -180 and 180')

    if lat_min < 0 or lat_min > 90:
        raise ValueError('latitude should be between 0 and 90')

    if lat_max < 0 or lat_max > 90:
        raise ValueError('latitude should be between 0 and 90')

    if days < 1 or days > 32:
        raise ValueError('days should be between 1 and 32')

    folder_date = utc_now
    if utc_now.hour > 18:
        folder_date = folder_date.replace(hour=18)

    elif utc_now.hour > 12:
        folder_date = folder_date.replace(hour=12)

    elif utc_now.hour > 6:
        folder_date = folder_date.replace(hour=6)

    else:
        folder_date = folder_date.replace(hour=0)

        # Try to find the first available data set
    data_set_attempts = 0
    while True:

        # build file names and paths
        server_dir = '%(y)04d%(m)02d%(d)02d%(h)02d' % {
            "y": folder_date.year,
            "m": folder_date.month,
            "d": folder_date.day,
            "h": folder_date.hour
        }

        # check whether this server set exists
        url_root = 'http://www.nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl'
        folder_url = url_root + '?dir=%2Fgfs.' + server_dir
        try:
            response = urllib2.urlopen(folder_url)
            response.read()  # if this does not raise an exception, this data set is accessible
            break

        except urllib2.HTTPError, e:

            if e.code == 500:
                # server throws code '500' in case the folder is not accessible.
                # this usually means the set is not available yet.
                print 'Data set \'' + server_dir + '\' is not (yet) available. ' \
                                                   'Attempting to download the preceding set.'
                data_set_attempts += 1

                # Subtract 6 hours from the date to target the previous set
                folder_date = folder_date + timedelta(hours = -6)

            else:
                pass

            if data_set_attempts >= 2:
                raise IOError('Unable to find a suitable server set')

    destination_file_name_partial_ext = '.grb.partial'
    destination_file_name_ext = '.grb'
    destination_file_name = '%(y)04d%(mon)02d%(d)02d_%(h)02d%(min)02d%(s)02d' % {
        'y': now.year,
        'mon': now.month,
        'd': now.day,
        'h': now.hour,
        'min': now.minute,
        's': now.second
    }

    # Calculate the offset, so we ignore passed hours
    delta = utc_now - folder_date
    source_file_offset, remainder = divmod(delta.seconds, 3600)

    # Download the files to our destination file
    print 'Downloading set \'' + server_dir + '\' to \'' + destination_file_name + destination_file_name_ext + '\''
    with open(os.path.join(path, destination_file_name + destination_file_name_partial_ext), "wb") as destination_file:
        for num in range(0, source_file_count):

            # Determine whether this 'hour' is available
            # we calculate this to prevent unnecessary server requests
            index = num + source_file_offset

            if index >= 240:
                interval = 12

            elif index >= 120:
                interval = 3

            else:
                interval = 0

            if interval > 0 and index % interval > 0:
                # This hour is unavailable at the server.
                print 'Skipping    %(i)d / %(t)d  Data is unavailable at server' % {
                    'i': num + 1,
                    't': source_file_count
                }
                continue

            # Passed the interval test.
            source_file = 'gfs.t%(h)02dz.pgrb2.0p25.f%(n)03d' % \
                          {
                              "h": folder_date.hour,
                              "n": index
                          }

            # build the request url
            url = url_root \
                  + '?file=' + source_file \
                  + '&lev_10_m_above_ground=on' \
                  + '&lev_2_m_above_ground=on' \
                  + '&lev_mean_sea_level=on' \
                  + '&lev_entire_atmosphere=on' \
                  + '&lev_surface=on'

            if download_gust == '1':
                url += '&var_GUST=on'

            if download_precipitation == '1':
                url += '&var_APCP=on'

            if download_humidity == '1':
                url += '&var_RH=on'

            if download_tmp == '1':
                url += '&var_TMP=on'

            if download_cape == '1':
                url += '&var_CAPE=on'

            if download_pressure == '1':
                url += '&var_PRMSL=on'

            if download_min_max_temp == '1':
                url += '&var_TMIN=on&var_TMAX=on'

            if download_wind == '1':
                url += '&var_VGRD=on&var_UGRD=on'

            if download_cloud_cover == '1':
                url += '&var_TCDC=on'

            url += '&subregion=' + \
                   '&leftlon=' + str(lon_min) + \
                   '&rightlon=' + str(lon_max) + \
                   '&toplat=' + str(lat_min) + \
                   '&bottomlat=' + str(lat_max)

            url += '&dir=%2Fgfs.' + server_dir

            print 'Downloading %(i)d / %(t)d %(f)s' % {
                'i': num + 1,
                't': source_file_count,
                'f': source_file
            }

            # open the response and write it to disk
            try:
                response = urllib2.urlopen(url)
                destination_file.write(response.read())
            except urllib2.HTTPError, e:
                # 404 means the file does not exits.
                # usually this indicates the
                if e.code != 404:
                    pass

    # remove the partial ext
    os.rename(os.path.join(path, destination_file_name + destination_file_name_partial_ext),
              os.path.join(path, destination_file_name + destination_file_name_ext))

    print 'Download completed.'


def clean_folder():
    now = time.time()
    clean_days = int(conf.get('GRIB', 'clean_days'))

    # validate input parameters
    if clean_days < 1:
        raise ValueError('clean_days should at least be 1')

    print 'Cleaning folder \'' + path + '\'...'

    # loop trough files in the grib directory
    for filename in os.listdir(path):
        full_filename = os.path.join(path, filename)
        if os.path.isfile(full_filename):
            if filename.endswith('.partial'):
                # Partial file found. Probably from an aborted download
                print "PARTIAL: %(f)s" % {
                    'f': filename
                }
                try:
                    os.remove(full_filename)
                except OSError as e:
                    print 'Could not remove file: ' + str(e)

            elif os.stat(full_filename).st_mtime < now - clean_days * (60 * 60 * 24):
                # file is expired. Delete the file
                print "EXPIRED: %(f)s" % {
                    'f': filename
                }
                try:
                    os.remove(full_filename)
                except OSError as e:
                    print 'Could not remove file: ' + str(e)
            else:
                # file is not expired. Skip the file
                print "SKIPPED:  %(f)s" % {
                    'f': filename
                }

    print "Clean completed."


# download settings
paths = Paths()
conf = Conf(paths)
run_interval = int(conf.get('GRIB', 'run_interval'))
run_at_startup = conf.get('GRIB', 'run_at_startup')
clean = conf.get('GRIB', 'clean')
path = conf.get('GRIB', 'path')

if run_interval < 1:
    raise ValueError("Run_interval should at least be 1 minute.")

if not path:
    raise ValueError("Path property is mandatory.")

if not os.path.exists(path):
    raise EnvironmentError("Path does not exist")


# Schedule the task
schedule.every(run_interval).minutes.do(run_scheduled)

# Initially run
if run_at_startup == '1':
    schedule.run_all(0)
else:
    print 'First download is scheduled at ' + str(schedule.next_run())

# Await and run scheduled tasks
while True:

    schedule.run_pending()
    time.sleep(60)  # sleeping for a minute to save resources