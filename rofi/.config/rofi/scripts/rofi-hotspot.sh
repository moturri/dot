#!/usr/bin/env bash
# Compatible with Bash and Zsh

# === Safe Mode ===
set -e
set -u
set -o pipefail 2>/dev/null || true

# === Config ===
SESSION="m"
WIFI_INTERFACE="wlan0"
ROFI_PROMPT_ICON="󰌢"
ROFI_WINDOW_ICON="󰍹"

# === Profile and Environment ===
PROFILE="${1:-default}"
ENV_FILE="$HOME/.config/create_ap/env_$PROFILE"

if [ ! -f "$ENV_FILE" ]; then
	notify-send "Missing profile" "Could not find env file: $ENV_FILE"
	exit 1
fi

# shellcheck disable=SC1090
. "$ENV_FILE"

# === Functions ===

get_channel() {
	iw dev "$WIFI_INTERFACE" info 2>/dev/null | grep -oE 'channel [0-9]+' | awk '{print $2}' || true
}

notify_err() {
	notify-send "AP Error" "$1"
	exit 1
}

action_prompt() {
	printf '%s\n' "create_ap tmux a -s" "tmux a" | rofi -dmenu -i -p "$ROFI_PROMPT_ICON"
}

window_name_prompt() {
	echo "create_ap" | rofi -dmenu -p "$ROFI_WINDOW_ICON"
}

create_ap_tmux_window() {
	local win_name="$1"
	local channel
	channel=$(get_channel)

	[ -z "$channel" ] && notify_err "Wi-Fi channel not found on $WIFI_INTERFACE."

	tmux has-session -t "$SESSION" 2>/dev/null || tmux new-session -d -s "$SESSION"

	# Exit after create_ap exits (no lingering shell)
	tmux new-window -t "$SESSION:" -n "$win_name" \
		"sudo create_ap '$WIFI_INTERFACE' '$WIFI_INTERFACE' '$SSID' '$PASSWORD' -c $channel"

	tmux attach-session -t "$SESSION"
}

to_lower() {
	echo "$1" | tr '[:upper:]' '[:lower:]'
}

main() {
	local action
	action=$(action_prompt) || exit 1

	case "$action" in
	"create_ap tmux a -s")
		local win_name
		win_name=$(window_name_prompt) || exit 1
		[ -n "$win_name" ] && create_ap_tmux_window "$win_name"
		;;
	"tmux a")
		tmux attach-session -t "$SESSION" || notify_err "No tmux session '$SESSION'"
		;;
	*)
		exit 1
		;;
	esac
}

main
