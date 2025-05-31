#!/usr/bin/env bash
set -euo pipefail

lock_cmd="${LOCK_CMD:-i3lock -c 000000}"

lock="󰌾  Lock"
sleep="󰒲  Sleep"
logout="  Logout"
reboot="󱑞  Reboot"
shutdown="󰐥  Shutdown"
cancel="󰜺  Cancel"

options=("$lock" "$sleep" "$logout" "$reboot" "$shutdown" "$cancel")

choice=$(printf '%s\n' "${options[@]}" | rofi -dmenu -i -p "󰟀 " -lines "${#options[@]}")

confirm_action() {
  local prompt="$1"
  rofi -dmenu -i -p "$prompt" -lines 2 <<<$'Yes\nNo'
}

case "$choice" in
"$lock")
  $lock_cmd
  ;;
"$sleep")
  [[ "$(confirm_action 'Suspend system?')" == "Yes" ]] && systemctl suspend
  ;;
"$logout")
  [[ "$(confirm_action 'Logout from Qtile?')" == "Yes" ]] && qtile cmd-obj -o cmd -f shutdown
  ;;
"$reboot")
  [[ "$(confirm_action 'Reboot system?')" == "Yes" ]] && systemctl reboot
  ;;
"$shutdown")
  [[ "$(confirm_action 'Shutdown system?')" == "Yes" ]] && systemctl poweroff
  ;;
*)
  exit 0
  ;;
esac
