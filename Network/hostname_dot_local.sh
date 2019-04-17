#!/bin/bash
#echo "adds or deletes .local in /etc/hosts."
#echo "Example: bash hostname_dot_local.sh y"

hname=`hostname -f`
hlname="${hname}.local"
#10.10.10.1 is the fixed address of the host (look for it in /etc/dhcpcd.conf) 
line="10.10.10.1	${hname}.local ${hname}"

response=$1

if [[ "$response" =~ ^([yY][eE][sS]|[yY])+$ ]]; then
	if grep -q -F "$hlname" /etc/hosts; then
	  echo
	else
	  oldline=$(grep -F '.local' /etc/hosts)
	  
	  if grep -q -F '.local' /etc/hosts
	  then 
		sudo sed -i "s/${oldline}/${line}/g" /etc/hosts
	  else
		sudo sed -i -e '$ a\' -e "${line}" /etc/hosts
	  fi
	fi
else
	if grep -q -F "$hlname" /etc/hosts
	then
	  oldline=$(grep -F '.local' /etc/hosts)
	  sudo sed -i "/${oldline}/d" /etc/hosts
	fi
fi
