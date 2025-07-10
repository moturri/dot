#!/usr/bin/env bash

set -euo pipefail

SESSION="${1:-m}"
WIFI_INTERFACE="wlan0"
DEFAULT_PROFILE="default"
PROFILE="${2:-$DEFAULT_PROFILE}"
ENV_FILE="$HOME/.config/create_ap/env_$PROFILE"

for cmd in tmux rofi notify-send sudo-rs create_ap iw alacritty; do
	command -v "$cmd" >/dev/null || {
		notify-send "❌ Missing Dependency" "Required command not found: $cmd"
		exit 1
	}
done

if [[ ! -f "$ENV_FILE" ]]; then
	notify-send "❌ Missing Profile" "Could not find env file:\n$ENV_FILE"
	exit 1
fi

if [[ $(stat -c "%a" "$ENV_FILE") -gt 600 ]]; then
	notify-send "⚠️ Insecure Permissions" \
		"Environment file is too permissive:\n$ENV_FILE\nRun: chmod 600 \"$ENV_FILE\""
fi

. "$ENV_FILE"

if [[ -z "${SSID:-}" || -z "${PASSWORD:-}" ]]; then
	notify-send "❌ Missing Variables" \
		"SSID or PASSWORD not set in:\n$ENV_FILE"
	exit 1
fi

get_channel() {
	iw dev "$WIFI_INTERFACE" info 2>/dev/null | grep -oE 'channel [0-9]+' | awk '{print $2}' || true
}

notify_err() {
	notify-send "❌ AP Error" "$1"
	exit 1
}

create_ap_tmux() {
	local channel
	channel=$(get_channel)

	if [[ -z "$channel" ]]; then
		channel=$(rofi -dmenu -p "No channel detected. Enter manually (e.g. 1,6,11):")
		[[ -z "$channel" ]] && notify_err "No channel provided."
	fi

	if ! tmux has-session -t "$SESSION" 2>/dev/null; then
		tmux new-session -d -s "$SESSION"
	fi

	tmux new-window -t "$SESSION:" -n "create_ap" \
		"sudo-rs create_ap '$WIFI_INTERFACE' '$WIFI_INTERFACE' '$SSID' '$PASSWORD' -c $channel; read -n1 -r -p 'Press any key to exit...'"
	tmux attach-session -t "$SESSION"
}

attach_tmux_session() {
	tmux attach-session -t "$SESSION" || notify_err "No tmux session '$SESSION' found."
}

launch_tmux_alacritty() {
	tmux has-session -t "$SESSION" 2>/dev/null || tmux new-session -d -s "$SESSION"
	alacritty -e tmux attach-session -t "$SESSION" &
}

main() {
	local options=("󰖩  Create Hotspot" "  Attach to Session" "󰯅  Launch Session Only")
	local choice

	choice=$(printf '%s\n' "${options[@]}" | rofi -dmenu -i -p "󰀂 create_ap")

	case "$choice" in
	"󰖩  Create Hotspot")
		create_ap_tmux
		;;
	"  Attach to Session")
		attach_tmux_session
		;;
	"󰯅  Launch Session Only")
		launch_tmux_alacritty
		;;
	*)
		exit 0
		;;
	esac
}

main
