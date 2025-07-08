#!/usr/bin/env bash

set -euo pipefail

SESSION="${1:-m}"
WIFI_INTERFACE="wlan0"
DEFAULT_PROFILE="default"

PROFILE="${2:-$DEFAULT_PROFILE}"
ENV_FILE="$HOME/.config/create_ap/env_$PROFILE"

for cmd in tmux rofi notify-send sudo-rs create_ap iw alacritty; do
	command -v "$cmd" >/dev/null || {
		notify-send "Missing Dependency" "Required command not found: $cmd"
		exit 1
	}
done

if [[ ! -f "$ENV_FILE" ]]; then
	notify-send "Missing Profile" "Could not find env file:\n$ENV_FILE"
	exit 1
fi

if [[ $(stat -c "%a" "$ENV_FILE") -gt 600 ]]; then
	notify-send "Warning" "Environment file is too permissive:\n$ENV_FILE\nRecommended: chmod 600"
fi

. "$ENV_FILE"

[[ -z "${SSID:-}" || -z "${PASSWORD:-}" ]] && {
	notify-send "Missing Variables" "SSID or PASSWORD not set in:\n$ENV_FILE"
	exit 1
}

get_channel() {
	iw dev "$WIFI_INTERFACE" info 2>/dev/null | grep -oE 'channel [0-9]+' | awk '{print $2}' || true
}

notify_err() {
	notify-send "AP Error" "$1"
	exit 1
}

create_ap_tmux() {
	local channel
	channel=$(get_channel)

	if [[ -z "$channel" ]]; then
		channel=$(rofi -dmenu -p "No channel found. Enter channel manually (e.g. 1, 6, 11):")
		[[ -z "$channel" ]] && notify_err "No channel provided."
	fi

	tmux has-session -t "$SESSION" 2>/dev/null || tmux new-session -d -s "$SESSION"

	tmux new-window -t "$SESSION:" -n "create_ap" \
		"sudo-rs create_ap '$WIFI_INTERFACE' '$WIFI_INTERFACE' '$SSID' '$PASSWORD' -c $channel; read -n1 -r -p 'Press any key to exit...'"

	tmux attach-session -t "$SESSION"
}

launch_tmux_alacritty() {
	tmux has-session -t "$SESSION" 2>/dev/null || tmux new-session -d -s "$SESSION"
	alacritty -e tmux attach-session -t "$SESSION" &
}

main() {
	local options="Create Hotspot\nAttach to Session\nLaunch Session Only"
	local action
	action=$(echo -e "$options" | rofi -dmenu -i -p "create_ap")

	case "$action" in
	"Create Hotspot")
		create_ap_tmux
		;;
	"Attach to Session")
		tmux attach-session -t "$SESSION" || notify_err "No tmux session '$SESSION' found."
		;;
	"Launch Session Only")
		launch_tmux_alacritty
		;;
	esac
}

main
