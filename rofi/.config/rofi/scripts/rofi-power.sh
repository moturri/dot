#!/bin/bash

lock="󰌾  Lock"
logout="  Logout"
reboot="󱑞  Reboot"
shutdown="󰐥  Shutdown"
cancel="󰜺  Cancel"

options=(
	"$lock"
	"$logout"
	"$reboot"
	"$shutdown"
	"$cancel"
)

choice=$(printf '%s\n' "${options[@]}" | rofi -dmenu -i -p "Power Menu")

confirm_exit() {
	echo -e "Yes\nNo" | rofi -dmenu -i -p "Are you sure?"
}

case "$choice" in
"$lock")
	i3lock -c 000000
	;;
"$logout")
	qtile cmd-obj -o cmd -f shutdown
	;;
"$reboot")
	[[ "$(confirm_exit)" == "Yes" ]] && reboot
	;;
"$shutdown")
	[[ "$(confirm_exit)" == "Yes" ]] && poweroff
	;;
*)
	exit 0
	;;
esac
