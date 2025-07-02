#!/usr/bin/env bash
# This script is compatible with both bash and zsh

# === Set safe options ===
set -e
set -u
set -o pipefail 2>/dev/null || true # pipefail may not exist in zsh

# === Configuration ===
WIFI_INTERFACE="wlan0"
DEFAULT_PROFILE="default"
ENV_DIR="$HOME/.config/create_ap"

# === Functions ===

die() {
	echo "Error: $1" >&2
	exit 1
}

get_channel() {
	iw dev "$WIFI_INTERFACE" info 2>/dev/null | grep -oE 'channel [0-9]+' | awk '{print $2}' || true
}

load_env() {
	local profile="$1"
	local env_file="$ENV_DIR/env_$profile"
	if [ ! -f "$env_file" ]; then
		die "Missing profile: $env_file"
	fi
	# shellcheck disable=SC1090
	. "$env_file"
}

to_lower() {
	# Works in both bash and zsh
	echo "$1" | tr '[:upper:]' '[:lower:]'
}

start_ap() {
	local channel
	channel=$(get_channel)

	echo "Starting Wi-Fi Access Point:"
	echo "  Interface : $WIFI_INTERFACE"
	echo "  SSID      : $SSID"
	echo "  Password  : [hidden]"
	[ -n "$channel" ] && echo "  Channel   : $channel"
	echo

	sudo create_ap "$WIFI_INTERFACE" "$WIFI_INTERFACE" "$SSID" "$PASSWORD" ${channel:+-c "$channel"}
}

# === Main ===

PROFILE="${1:-$DEFAULT_PROFILE}"

echo "=== create_ap (profile: $PROFILE) ==="
load_env "$PROFILE"

printf "Start access point now? [y/N]: "
read -r confirm
confirm=$(to_lower "$confirm")

if [ "$confirm" = "y" ]; then
	start_ap
else
	echo "Aborted."
	exit 0
fi
