#!/usr/bin/env bash
set -euo pipefail

EXTERNAL_DISPLAY="${1:-DP-1}"
INTERNAL_DISPLAY="${INTERNAL_DISPLAY:-eDP-1}"
ROFI_CMD="rofi -dmenu -i -p"

for cmd in xrandr notify-send rofi qtile; do
	command -v "$cmd" >/dev/null || {
		notify-send " Missing required command: $cmd"
		exit 1
	}
done

main() {
	local options="   Auto (Left)
   Auto (Right)
   󰍶  Disconnect"
	local action

	action=$(echo -e "$options" | $ROFI_CMD "  ") || exit 0

	case "$action" in
	*"Auto (Left)")
		if ! xrandr | grep -q "^$EXTERNAL_DISPLAY connected"; then
			notify-send "Display Setup " "  $EXTERNAL_DISPLAY is not connected." -t 5000
			exit 1
		fi
		xrandr --output "$EXTERNAL_DISPLAY" --auto --left-of "$INTERNAL_DISPLAY"
		notify-send "  $EXTERNAL_DISPLAY set to the left of $INTERNAL_DISPLAY." -t 6000
		;;
	*"Auto (Right)")
		if ! xrandr | grep -q "^$EXTERNAL_DISPLAY connected"; then
			notify-send "Display Setup " "  $EXTERNAL_DISPLAY is not connected." -t 5000
			exit 1
		fi
		xrandr --output "$EXTERNAL_DISPLAY" --auto --right-of "$INTERNAL_DISPLAY"
		notify-send "  $EXTERNAL_DISPLAY set to the right of $INTERNAL_DISPLAY." -t 6000
		;;

	*"Disconnect")
		xrandr --output "$EXTERNAL_DISPLAY" --off
		notify-send "  Disconnected $EXTERNAL_DISPLAY." -t 6000
		;;
	*)
		notify-send "  Invalid option selected." -t 4000
		exit 1
		;;
	esac

	sleep 1 && qtile cmd-obj -o cmd -f restart
}

main
