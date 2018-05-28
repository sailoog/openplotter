#!/bin/bash
path=$1
sudo dpkg -i $path
read -p "Finished. If the process has been successful, the system will automatically restart in a few seconds. If there have been failures, check the log and close this window."