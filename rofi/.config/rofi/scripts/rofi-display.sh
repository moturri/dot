#!/bin/bash

EXTERNAL_DISPLAY="DP1"

connect_display() {
	local position=$1

	xrandr --output "$EXTERNAL_DISPLAY" --auto "--${position}-of" "eDP1"

	notify-send "Display" "Monitor connected $position of laptop" -t 6000
}

disconnect_display() {
	xrandr --output "$EXTERNAL_DISPLAY" --off
	notify-send "Display" "Monitor disconnected" -t 6000
}

refresh_qtile() {
	sleep 0.5
	qtile cmd-obj -o cmd -f restart
}

main() {
	action=$(printf "Connect 󰍺 \nDisconnect 󰍺 " | rofi -dmenu -i -p "󰌢 󱘖 󰍺 ")

	case "$action" in
	"Connect 󰍺 ")
		position=$(printf "left\nright" | rofi -dmenu -i -p "󰌢 󱘖 󰍺 ")
		[[ -z "$position" ]] && exit 0

		connect_display "$position"
		refresh_qtile
		;;

	"Disconnect 󰍺 ")
		disconnect_display
		refresh_qtile
		;;

	*)
		exit 0
		;;
	esac
}

main
