#!/bin/bash

lock="󰌾  Lock"
sleep="󰒲  Sleep"
logout="  Logout"
reboot="󱑞  Reboot"
shutdown="󰐥  Shutdown"
cancel="󰜺  Cancel"

options=("$lock" "$sleep" "$logout" "$reboot" "$shutdown" "$cancel")

choice=$(printf '%s\n' "${options[@]}" | rofi -dmenu -i -p "󰟀 " -lines ${#options[@]})

confirm_action() {
	local prompt="$1"
	echo -e "Yes\nNo" | rofi -dmenu -i -p "$prompt" -lines 2
}

case "$choice" in
"$lock")
	i3lock -c 000000
	;;
"$sleep")
	if [[ "$(confirm_action "Suspend system?")" == "Yes" ]]; then
		systemctl suspend
	fi
	;;
"$logout")
	if [[ "$(confirm_action "Logout from Qtile?")" == "Yes" ]]; then
		qtile cmd-obj -o cmd -f shutdown || pkill -TERM qtile
	fi
	;;
"$reboot")
	if [[ "$(confirm_action "Reboot system?")" == "Yes" ]]; then
		systemctl reboot || reboot
	fi
	;;
"$shutdown")
	if [[ "$(confirm_action "Shutdown system?")" == "Yes" ]]; then
		systemctl poweroff || poweroff
	fi
	;;
*)
	exit 0
	;;
esac
