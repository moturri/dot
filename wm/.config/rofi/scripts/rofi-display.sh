#!/usr/bin/env bash
set -euo pipefail

EXTERNAL_DISPLAY="${1:-DP-1}"
INTERNAL_DISPLAY="${2:-${INTERNAL_DISPLAY:-eDP-1}}"
ROFI_CMD="rofi -dmenu -i -p"

for cmd in xrandr notify-send rofi qtile; do
	command -v "$cmd" >/dev/null || {
		notify-send "Display Setup" "Missing required command: $cmd" -u critical
		exit 1
	}
done

is_connected() {
	xrandr | grep -qE "^${EXTERNAL_DISPLAY} connected"
}

main() {
	local options="   Auto (Left)
   Auto (Right)
   󰍶  Disconnect"
	local action

	action=$(printf '%s\n' "$options" | $ROFI_CMD "  ") || exit 0

	case "$action" in
	*"Auto (Left)"*)
		if ! is_connected; then
			notify-send "Display Setup" "  ${EXTERNAL_DISPLAY} is not connected." -t 5000
			exit 1
		fi
		xrandr --output "$EXTERNAL_DISPLAY" --auto --left-of "$INTERNAL_DISPLAY"
		notify-send "Display Setup" "  ${EXTERNAL_DISPLAY} set to the left of ${INTERNAL_DISPLAY}." -t 6000
		;;
	*"Auto (Right)"*)
		if ! is_connected; then
			notify-send "Display Setup" "  ${EXTERNAL_DISPLAY} is not connected." -t 5000
			exit 1
		fi
		xrandr --output "$EXTERNAL_DISPLAY" --auto --right-of "$INTERNAL_DISPLAY"
		notify-send "Display Setup" "  ${EXTERNAL_DISPLAY} set to the right of ${INTERNAL_DISPLAY}." -t 6000
		;;
	*"Disconnect"*)
		xrandr --output "$EXTERNAL_DISPLAY" --off
		notify-send "Display Setup" "  Disconnected ${EXTERNAL_DISPLAY}." -t 6000
		;;
	*)
		notify-send "Display Setup" "  Invalid option selected." -t 4000
		exit 1
		;;
	esac

	sleep 1
	if ! qtile cmd-obj -o cmd -f restart >/dev/null 2>&1; then
		notify-send "Display Setup" "  qtile restart failed; restart manually if needed." -t 6000
	fi
}

main
