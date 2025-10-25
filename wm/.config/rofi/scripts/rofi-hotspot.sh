#!/usr/bin/env bash

set -euo pipefail

declare -A DEFAULTS=(
	[session]="m"
	[profile]="default"
)

SESSION="${1:-${DEFAULTS[session]}}"
PROFILE="${2:-${DEFAULTS[profile]}}"
ENV_FILE="$HOME/.config/create_ap/env_$PROFILE"

rofi_err() {
	rofi -dmenu -p " $1" <<<"" >/dev/null
	exit 1
}

notify_warn() {
	notify-send "AP Warning" " $1"
}

if ! locale | grep -q "UTF-8"; then
	export LANG="en_US.UTF-8"
	notify_warn "Locale forced to UTF-8 for proper icon rendering."
fi

deps=(tmux rofi create_ap iw kitty)
SUDO_CMD="sudo-rs"
if ! command -v "$SUDO_CMD" &>/dev/null; then
	SUDO_CMD="sudo"
fi
deps+=("$SUDO_CMD")

for cmd in "${deps[@]}"; do
	command -v "$cmd" >/dev/null || rofi_err "Missing required command: $cmd"
done

detect_iface() {
	iw dev 2>/dev/null | awk '/Interface/ {print $2; exit}'
}
WIFI_INTERFACE="$(detect_iface || true)"
[[ -z "$WIFI_INTERFACE" ]] && rofi_err "No wireless interface detected via iw dev."

if [[ ! -f "$ENV_FILE" ]]; then
	rofi_err "Missing profile env file:\n$ENV_FILE"
fi

if [[ $(stat -c "%a" "$ENV_FILE") -gt 600 ]]; then
	notify_warn "Env file too permissive:\n$ENV_FILE\nRun: chmod 600 \"$ENV_FILE\""
fi

# shellcheck source=/dev/null
. "$ENV_FILE"

trim() {
	local var="$1"
	var="${var#"${var%%[![:space:]]*}"}"
	echo "${var%"${var##*[![:space:]]}"}"
}

SSID="$(trim "${SSID:-}")"
PASSWORD="$(trim "${PASSWORD:-}")"

if [[ -z "$SSID" || -z "$PASSWORD" ]]; then
	rofi_err "SSID or PASSWORD not set in:\n$ENV_FILE"
fi

cleanup() {
	trap - INT TERM EXIT
}
trap cleanup INT TERM EXIT

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
		"$SUDO_CMD create_ap '$WIFI_INTERFACE' '$WIFI_INTERFACE' '$SSID' '$PASSWORD' -c $channel; read -n1 -r -p 'Press any key to exit...'"
	tmux attach-session -t "$SESSION"
}

attach_tmux_session() {
	tmux attach-session -t "$SESSION" || rofi_err "No tmux session '$SESSION' found."
}

launch_tmux_kitty() {
	tmux has-session -t "$SESSION" 2>/dev/null || tmux new-session -d -s "$SESSION"
	kitty -e tmux attach-session -t "$SESSION" &
}

main() {
	local options=("󰖩  Create Hotspot" "  Attach to Session" "󰯅  Launch Session Only")
	local choice
	choice=$(printf '%s\n' "${options[@]}" | rofi -dmenu -i -p "󰀂 ")

	case "$choice" in
	"󰖩  Create Hotspot") create_ap_tmux ;;
	"  Attach to Session") attach_tmux_session ;;
	"󰯅  Launch Session Only") launch_tmux_kitty ;;
	*) exit 0 ;;
	esac
}

main
