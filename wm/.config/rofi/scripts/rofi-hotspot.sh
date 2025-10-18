#!/usr/bin/env bash

set -euo pipefail

SESSION="${1:-m}"
WIFI_INTERFACE="wlan0"
DEFAULT_PROFILE="default"
PROFILE="${2:-$DEFAULT_PROFILE}"
ENV_FILE="$HOME/.config/create_ap/env_$PROFILE"

# --- rofi-based errors ---
rofi_err() {
	rofi -dmenu -p " $1" <<<"" >/dev/null
	exit 1
}

# --- passive warnings ---
notify_warn() {
	notify-send "AP Warning" " $1"
}

# --- dependency check ---
for cmd in tmux rofi sudo-rs create_ap iw kitty; do
	command -v "$cmd" >/dev/null || rofi_err "Missing required command: $cmd"
done

# --- env file checks ---
if [[ ! -f "$ENV_FILE" ]]; then
	rofi_err "Missing profile env file:\n$ENV_FILE"
fi

if [[ $(stat -c "%a" "$ENV_FILE") -gt 600 ]]; then
	notify_warn "Env file too permissive:\n$ENV_FILE\nRun: chmod 600 \"$ENV_FILE\""
fi

# shellcheck source=/dev/null
. "$ENV_FILE"

if [[ -z "${SSID:-}" || -z "${PASSWORD:-}" ]]; then
	rofi_err "SSID or PASSWORD not set in:\n$ENV_FILE"
fi

# --- functions ---
get_channel() {
	iw dev "$WIFI_INTERFACE" info 2>/dev/null | grep -oE 'channel [0-9]+' | awk '{print $2}' || true
}

create_ap_tmux() {
	local channel
	channel=$(get_channel)

	if [[ -z "$channel" ]]; then
		channel=$(rofi -dmenu -p "󰖩 No channel detected. Enter manually (1,6,11):")
		[[ -z "$channel" ]] && rofi_err "No channel provided."
	fi

	if ! tmux has-session -t "$SESSION" 2>/dev/null; then
		tmux new-session -d -s "$SESSION"
	fi

	tmux new-window -t "$SESSION:" -n "create_ap" \
		"sudo-rs create_ap '$WIFI_INTERFACE' '$WIFI_INTERFACE' '$SSID' '$PASSWORD' -c $channel; read -n1 -r -p 'Press any key to exit...'"
	tmux attach-session -t "$SESSION"
}

attach_tmux_session() {
	tmux attach-session -t "$SESSION" || rofi_err "No tmux session '$SESSION' found."
}

launch_tmux_kitty() {
	tmux has-session -t "$SESSION" 2>/dev/null || tmux new-session -d -s "$SESSION"
	kitty -e tmux attach-session -t "$SESSION" &
}

# --- main menu ---
main() {
	local options=("󰖩  Create Hotspot" "  Attach to Session" "󰯅  Launch Session Only")
	local choice

	choice=$(printf '%s\n' "${options[@]}" | rofi -dmenu -i -p "󰀂 ")

	case "$choice" in
	"󰖩  Create Hotspot")
		create_ap_tmux
		;;
	"  Attach to Session")
		attach_tmux_session
		;;
	"󰯅  Launch Session Only")
		launch_tmux_kitty
		;;
	*)
		exit 0
		;;
	esac
}

main
