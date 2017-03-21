#!/bin/bash
echo
echo "UPDATING PACKAGES..."
echo
sudo apt-get update
echo
echo "INSTALLING OPENCPN PLUGINS..."
echo
sudo apt-get install -y oesenc-pi opencpn-plugin-aisradar opencpn-plugin-br24radar opencpn-plugin-calculator opencpn-plugin-climatology opencpn-plugin-climatology-data opencpn-plugin-celestial opencpn-plugin-dr opencpn-plugin-draw  opencpn-plugin-gradar opencpn-plugin-gxradar opencpn-plugin-iacfleet opencpn-plugin-launcher opencpn-plugin-logbookkonni opencpn-plugin-objsearch opencpn-plugin-ocpndebugger opencpn-plugin-otcurrent opencpn-plugin-polar opencpn-plugin-projections opencpn-plugin-rotationctrl opencpn-plugin-route opencpn-plugin-rtlsdr opencpn-plugin-s63 opencpn-plugin-sar opencpn-plugin-squiddio opencpn-plugin-statusbar opencpn-plugin-sweepplot opencpn-plugin-vdr opencpn-plugin-watchdog opencpn-plugin-weatherfax opencpn-plugin-weatherrouting
echo
read -p "FINISHED PRESS ENTER TO EXIT"
