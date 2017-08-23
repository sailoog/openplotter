#!/bin/bash
echo
echo "APPLYING DEFAULT SETTINGS..."
echo
cd ~/.config/pcmanfm/LXDE-pi
echo "[*]" > desktop-items-0.conf
echo "wallpaper_mode=center" >> desktop-items-0.conf
echo "wallpaper_common=1" >> desktop-items-0.conf
echo "wallpaper=/usr/share/raspberrypi-artwork/openplotter_RPI_desktop.png" >> desktop-items-0.conf
echo "desktop_bg=#d6d6d3d3dede" >> desktop-items-0.conf
echo "desktop_fg=#000000000000" >> desktop-items-0.conf
echo "desktop_shadow=#d6d6d3d3dede" >> desktop-items-0.conf
echo "desktop_font=Roboto Light 12" >> desktop-items-0.conf
echo "show_wm_menu=0" >> desktop-items-0.conf
echo "sort=mtime;ascending;" >> desktop-items-0.conf
echo "show_documents=0" >> desktop-items-0.conf
echo "show_trash=0" >> desktop-items-0.conf
echo "show_mounts=0" >> desktop-items-0.conf
echo "prefs_app=pipanel" >> desktop-items-0.conf
echo -e '[Desktop Entry]\nName=OpenPlotter debugging\nExec=lxterminal -e openplotter\nIcon=/home/pi/.config/openplotter/openplotter_debug.ico\nStartupNotify=true\nCategories=OpenPlotter\nTerminal=false\nType=Application\nVersion=1.0' > /home/pi/.local/share/applications/openplotter_debug.desktop
echo
echo "DELETING UNUSED ICONS..."
echo
sudo bash -c 'echo -e "[Desktop Entry]\nName=OpenCPN\nComment=Open source chart plotter / navigator\nExec=opencpn\nIcon=opencpn\nStartupNotify=true\nCategories=OpenPlotter\nTerminal=false\nType=Application\nVersion=1.0" > /usr/share/applications/opencpn.desktop'
sudo rm -rf /usr/share/raspi-ui-overrides/applications/magpi.desktop
sudo rm -rf /usr/share/raspi-ui-overrides/applications/raspi_resources.desktop
sudo rm -rf /usr/share/raspi-ui-overrides/applications/help.desktop
echo
echo "DISABLING SCREENSAVER..."
echo
sudo bash -c 'echo -e "\n@xset s 0 0\n@xset s noblank\n@xset s noexpose\n@xset dpms 0 0 0\n" >> /home/pi/.config/lxsession/LXDE-pi/autostart'
echo
read -p "FINISHED, PRESS ENTER TO REBOOT SYSTEM."
shutdown -r now