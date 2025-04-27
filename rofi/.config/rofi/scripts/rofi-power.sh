#!/bin/bash

# Nerd Font icons with labels
lock="󰌾  Lock"
logout="  Logout"
reboot="󱑞  Reboot"
shutdown="󰐥  Shutdown"
cancel="󰜺  Cancel"

# Options array for the power menu
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

# Handle user selection
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
