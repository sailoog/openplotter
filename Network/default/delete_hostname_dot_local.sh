#!/bin/bash
hname=`hostname -f`
hlname="${hname}.local"
#10.10.10.1 is the fixed address of the host (look for it in /etc/dhcpcd.conf) 
line="10.10.10.1	${hname}.local ${hname}"

if grep -q -F "$hlname" /etc/hosts
then
  oldline=$(grep -F '.local' /etc/hosts)
  echo "delete line     '${oldline}'"
  sudo sed -i "/${oldline}/d" /etc/hosts
  echo "done"
fi
