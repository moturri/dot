#!/usr/bin/env bash
# Compatible with Bash and Zsh

# === Safe Mode ===
set -euo pipefail
set -o noclobber 2>/dev/null || true # Optional: prevent file overwrites

# === Config ===
SESSION="m"
WIFI_INTERFACE="wlan0"
DEFAULT_PROFILE="default"

# === Environment Setup ===
PROFILE="${1:-$DEFAULT_PROFILE}"
ENV_FILE="$HOME/.config/create_ap/env_$PROFILE"

# === Check if env file exists ===
if [[ ! -f "$ENV_FILE" ]]; then
	notify-send "Missing Profile" "Could not find env file:\n$ENV_FILE"
	exit 1
fi

# shellcheck disable=SC1090
. "$ENV_FILE"

# === Functions ===

get_channel() {
	iw dev "$WIFI_INTERFACE" info 2>/dev/null |
		grep -oE 'channel [0-9]+' |
		awk '{print $2}' ||
		true
}

notify_err() {
	local msg="$1"
	notify-send "AP Error" "$msg"
	exit 1
}

action_prompt() {
	printf '%s\n' "create_ap tmux new-window -t m" "tmux attach-session" |
		rofi -dmenu -i -p "create_ap"
}

window_name_prompt() {
	echo "create_ap" | rofi -dmenu -i -p "Window Name"
}

create_ap_tmux_window() {
	local win_name="$1"
	local channel
	channel=$(get_channel)

	if [[ -z "$channel" ]]; then
		notify_err "Wi-Fi channel not found on $WIFI_INTERFACE."
	fi

	# Start tmux session if not already running
	if ! tmux has-session -t "$SESSION" 2>/dev/null; then
		tmux new-session -d -s "$SESSION"
	fi

	# Start create_ap in a new window
	tmux new-window -t "$SESSION:" -n "$win_name" \
		"sudo create_ap '$WIFI_INTERFACE' '$WIFI_INTERFACE' '$SSID' '$PASSWORD' -c $channel; read -n1 -r -p 'Press any key to exit...'" ||
		notify_err "Failed to start tmux window."

	tmux attach-session -t "$SESSION"
}

main() {
	local action
	action=$(action_prompt) || exit 0
	action="${action,,}" # normalize to lowercase

	case "$action" in
	"create_ap tmux new-window -t m")
		local win_name
		win_name=$(window_name_prompt) || exit 0
		[[ -n "$win_name" ]] && create_ap_tmux_window "$win_name"
		;;

	"tmux attach-session")
		tmux attach-session -t "$SESSION" || notify_err "No tmux session '$SESSION' found."
		;;

	*)
		notify-send "Unknown Action" "Unrecognized input: $action"
		exit 1
		;;
	esac
}

main
