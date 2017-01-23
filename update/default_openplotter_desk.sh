#!/bin/bash

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

echo "You have to logout/reboot to activate the settings."