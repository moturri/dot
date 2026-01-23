#!/usr/bin/env bash

set -euo pipefail

readonly SCRIPT_NAME="${0##*/}"
readonly SESSION="${1:-m}"
readonly PROFILE="${2:-default}"
readonly CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/create_ap"
readonly ENV_FILE="$CONFIG_DIR/env_$PROFILE"
readonly TMUX_AP_WINDOW_NAME="AP"
readonly TMUX_WIRED_AP_WINDOW_NAME="AP-Wired"

die() {
	rofi -dmenu -p "✗ [$SCRIPT_NAME] $1" <<<"" >/dev/null
	exit 1
}

notify() {
	command -v notify-send >/dev/null && notify-send "AP" "$1" || true
}

check_deps() {
	local missing=()
	local deps=(tmux rofi create_ap iw nmcli)

	for cmd in "${deps[@]}"; do
		command -v "$cmd" >/dev/null || missing+=("$cmd")
	done

	[[ ${#missing[@]} -eq 0 ]] || die "Missing: ${missing[*]}"

	# Detect sudo command
	if command -v sudo-rs >/dev/null; then
		echo "sudo-rs"
	elif command -v doas >/dev/null; then
		echo "doas"
	elif command -v sudo >/dev/null; then
		echo "sudo"
	else
		die "No privilege escalation tool found"
	fi
}

detect_wifi_interface() {
	local iface
	iface=$(iw dev 2>/dev/null | awk '/Interface/ {print $2; exit}')
	[[ -n "$iface" ]] || die "No wireless interface found"
	echo "$iface"
}

load_credentials() {
	[[ -f "$ENV_FILE" ]] || die "Config not found:\n$ENV_FILE"

	local perms
	perms=$(stat -c "%a" "$ENV_FILE" 2>/dev/null || stat -f "%Lp" "$ENV_FILE" 2>/dev/null)
	[[ "$perms" -le 600 ]] || notify "⚠ Insecure permissions on $ENV_FILE"

	# shellcheck source=/dev/null
	. "$ENV_FILE"

	SSID="${SSID// /}"
	PASSWORD="${PASSWORD// /}"

	[[ -n "$SSID" && -n "$PASSWORD" ]] || die "SSID/PASSWORD not set"
}

get_channel() {
	local channel
	channel=$(iw dev "$WIFI_INTERFACE" info 2>/dev/null | awk '/channel/ {print $2; exit}')

	if [[ -z "$channel" ]]; then
		channel=$(rofi -dmenu -p "󰖩 Channel (1/6/11):" -filter "6")
		[[ -n "$channel" ]] || die "No channel specified"
	fi

	echo "$channel"
}

select_wired_interface() {
	local devices
	devices=$(nmcli -t -f DEVICE,TYPE,STATE device status 2>/dev/null |
		awk -F: '$2=="ethernet" && $3=="connected" {print $1}')

	[[ -n "$devices" ]] || die "No active ethernet connection"

	local count
	count=$(echo "$devices" | wc -l)

	if [[ $count -eq 1 ]]; then
		echo "$devices"
	else
		local selected
		selected=$(echo "$devices" | rofi -dmenu -i -p "󰞹 Select interface:")
		[[ -n "$selected" ]] || exit 0
		echo "$selected"
	fi
}

ensure_session() {
	tmux has-session -t "$SESSION" 2>/dev/null || tmux new-session -d -s "$SESSION"
}

create_hotspot() {
	local channel
	channel=$(get_channel)

	ensure_session
	tmux new-window -t "$SESSION:" -n "$TMUX_AP_WINDOW_NAME" \
		"$SUDO_CMD create_ap '$WIFI_INTERFACE' '$WIFI_INTERFACE' '$SSID' '$PASSWORD' -c '$channel' || read -n1 -r -p 'Press any key...'"
}

create_wired_hotspot() {
	local channel upstream
	channel=$(get_channel)
	upstream=$(select_wired_interface)

	ensure_session
	tmux new-window -t "$SESSION:" -n "$TMUX_WIRED_AP_WINDOW_NAME" \
		"$SUDO_CMD create_ap '$WIFI_INTERFACE' '$upstream' '$SSID' '$PASSWORD' -c '$channel' || read -n1 -r -p 'Press any key...'"
}

main() {
	SUDO_CMD=$(check_deps)
	readonly SUDO_CMD
	WIFI_INTERFACE=$(detect_wifi_interface)
	readonly WIFI_INTERFACE
	load_credentials

	local -a options=(
		"󰖩  WiFi → WiFi"
		"󰈀  Ethernet → WiFi"
	)

	local choice
	choice=$(printf '%s\n' "${options[@]}" | rofi -dmenu -i -p "󰀂 Hotspot")

	case "$choice" in
	"${options[0]}") create_hotspot ;;
	"${options[1]}") create_wired_hotspot ;;
	*) exit 0 ;;
	esac
}

main
