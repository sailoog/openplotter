#!/bin/sh
response=$1
if [[ "$response" = "uninstall" ]]; then
	#no AP (set back to original setting)
	sudo cp dhcpcd.conf /etc
	sudo echo '#!/bin/sh' > ~/.openplotter/start-ap-managed-wifi.sh
	sudo cp network/interfaces /etc/network

	if [ -e /etc/network/interfaces.d/ap ]
	then
		sudo rm /etc/network/interfaces.d/ap
	fi

	if [ -e /etc/udev/rules.d/72-wireless.rules ]
	then
		sudo rm /etc/udev/rules.d/72-wireless.rules
	fi

	if [ -e /lib/dhcpcd/dhcpcd-hooks/10-wpa_supplicant_wlan9 ]
	then
		sudo rm /lib/dhcpcd/dhcpcd-hooks/10-wpa_supplicant_wlan9
		sudo cp ~/.config/openplotter/Network/dhcpcd-hooks/10-wpa_supplicant /lib/dhcpcd/dhcpcd-hooks
	fi

	if [ -e /etc/udev/rules.d/11-openplotter-usb0.rules ]
	then
		sudo rm /etc/udev/rules.d/11-openplotter-usb0.rules
	fi

	erg=$(systemctl status dnsmasq | grep 'enabled;')
	chrlen=${#erg}
	if [ $chrlen -gt 0 ]
	then
		sudo systemctl disable dnsmasq
	fi

	erg=$(systemctl status hostapd | grep 'enabled;')
	chrlen=${#erg}
	if [ $chrlen -gt 0 ]
	then
		sudo systemctl disable hostapd
	fi

else
	sudo cp dhcpcd.conf /etc
	sudo cp dnsmasq.conf /etc
	sudo cp .openplotter/start-ap-managed-wifi.sh ~/.openplotter
	sudo cp .openplotter/iptables.sh ~/.openplotter
	sudo cp .openplotter/start1.sh ~/.openplotter

	sudo cp hostapd/hostapd.conf /etc/hostapd
	sudo cp network/interfaces /etc/network
	sudo cp network/interfaces.d/ap /etc/network/interfaces.d
	sudo cp udev/rules.d/72-wireless.rules /etc/udev/rules.d

	if [ -e /lib/dhcpcd/dhcpcd-hooks/10-wpa_supplicant ]
	then
		sudo rm /lib/dhcpcd/dhcpcd-hooks/10-wpa_supplicant
		sudo cp ~/.config/openplotter/Network/dhcpcd-hooks/10-wpa_supplicant_wlan9 /lib/dhcpcd/dhcpcd-hooks
	fi

	if [ ! -e /etc/udev/rules.d/11-openplotter-usb0.rules ]
	then
		sudo cp udev/rules.d/11-openplotter-usb0.rules /etc/udev/rules.d
	fi

	erg=$(systemctl status dnsmasq | grep disabled)
	chrlen=${#erg}
	if [ $chrlen -gt 0 ]
	then
		sudo systemctl enable dnsmasq
	fi

	erg=$(systemctl status hostapd | grep disabled)
	chrlen=${#erg}
	if [ $chrlen -gt 0 ]
	then
		sudo systemctl enable hostapd
	fi	
fi

#old
	if [ -e /etc/udev/rules.d/72-static-name.rules ]
	then
		sudo rm /etc/udev/rules.d/72-static-name.rules
	fi
	
	oldline=$(grep -F 'net.ipv4.ip_forward' /etc/sysctl.conf)
	newline="net.ipv4.ip_forward=1"

	if [ "$oldline" = "$newline" ]; then
		sudo sed -i "s/${oldline}/#net.ipv4.ip_forward=1/g" /etc/sysctl.conf
	fi
