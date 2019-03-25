#!/bin/bash
#echo "This bash adds or appends a line to /etc/hosts to combine the hostname with .local."
#echo "Linux will be reachable from network by xxxx.local (xxxx is the hostname)."
hname=`hostname -f`
hlname="${hname}.local"
#10.10.10.1 is the fixed address of the host (look for it in /etc/dhcpcd.conf) 
line="10.10.10.1	${hname}.local ${hname}"

if grep -q -F "$hlname" /etc/hosts
then
  #echo "Line '${line}' is already in /etc/hosts"
  echo ""
else
  oldline=$(grep -F '.local' /etc/hosts)
  
  if grep -q -F '.local' /etc/hosts
  then 
    #echo "change '${oldline}' to"
	#echo "'${line}'"
    sudo sed -i "s/${oldline}/${line}/g" /etc/hosts
	#echo "done"
  else
	#echo "append '${line}'"
	sudo sed -i -e '$ a\' -e "${line}" /etc/hosts
	#echo "done"
  fi
fi
