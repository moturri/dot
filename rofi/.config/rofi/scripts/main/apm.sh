#!/bin/bash

WIFI_INTERFACE="wlan0"

SSID="*"
PASSWORD="********"

CHANNEL=$(iw dev "$WIFI_INTERFACE" info | grep -oP 'channel \K\d+')

if [ -z "$CHANNEL" ]; then
	echo "Could not determine channel for interface $WIFI_INTERFACE."
	echo "Please ensure you are connected to a Wi-Fi network."
	exit 1
fi

echo "Detected channel: $CHANNEL"

sudo create_ap "$WIFI_INTERFACE" "$WIFI_INTERFACE" "$SSID" "$PASSWORD" -c "$CHANNEL"
