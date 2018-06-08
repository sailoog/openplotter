#!/bin/bash
path=$1
sudo dpkg -i $path
read -p "If there have been failures, check the log and close this window."