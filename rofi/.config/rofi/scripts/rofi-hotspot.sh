#!/usr/bin/env bash
set -euo pipefail
# Config
SESSION="m"
WIFI_INTERFACE="wlan0"
SSID="*"
PASSWORD="********"
TERMINAL="alacritty" # or kitty, etc.
# Get current Wi-Fi channel
get_channel() {
	iw dev "$WIFI_INTERFACE" info | grep -oP 'channel \K\d+' || echo ""
}
# Prompt 1: Ask what to do
action_prompt() {
	printf '%s\n' "create_ap tmux a -s" "tmux a" | rofi -dmenu -i -p "󰌢  "
}
# Prompt 2: Ask for tmux window name
window_name_prompt() {
	rofi -dmenu -p "󰍹 " <<<"hotspot"
}
# Create tmux window and run sudo command
create_ap_tmux_window() {
	local win_name="$1"
	local channel
	channel=$(get_channel)
	if [ -z "$channel" ]; then
		notify-send "AP Error" "Wi-Fi channel not found."
		exit 1
	fi
	tmux new-window -t "$SESSION" -n "$win_name" \
		"sudo create_ap '$WIFI_INTERFACE' '$WIFI_INTERFACE' '$SSID' '$PASSWORD' -c '$channel'"
	notify-send "AP Started" "Window '$win_name' in session '$SESSION'"
}
# Attach to tmux session
attach_tmux_session() {
	"$TERMINAL" -e tmux attach -t "$SESSION"
}
main() {
	tmux has-session -t "$SESSION" 2>/dev/null || {
		notify-send "Tmux Error" "Session '$SESSION' not found. Start it first."
		exit 1
	}
	choice=$(action_prompt)
	[[ -z "$choice" ]] && exit 0
	case "$choice" in
	"create_ap tmux a -s")
		win_name=$(window_name_prompt)
		[[ -z "$win_name" ]] && exit 0
		create_ap_tmux_window "$win_name"
		;;
	"tmux a")
		attach_tmux_session
		;;
	*)
		exit 0
		;;
	esac
}
main
