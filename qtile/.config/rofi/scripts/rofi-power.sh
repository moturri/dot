#!/usr/bin/env bash
set -euo pipefail

# === Configuration ===
LOCK_CMD="${LOCK_CMD:-i3lock -c 000000}"
ROFI_CMD="rofi -dmenu -i -p"

# === Power Menu Options ===
lock="󰌾  Lock"
sleep="󰒲  Sleep"
logout="  Logout"
reboot="󱑞  Reboot"
shutdown="󰐥  Shutdown"
cancel="󰜺  Cancel"

options=("$lock" "$sleep" "$logout" "$reboot" "$shutdown" "$cancel")

# === Prompt User ===
choice=$(printf '%s\n' "${options[@]}" | $ROFI_CMD "󰟀 " -lines "${#options[@]}")

# === Confirmation Prompt ===
confirm_action() {
  local prompt="$1"
  echo -e "Yes\nNo" | $ROFI_CMD "$prompt"
}

# === Action Handling ===
case "$choice" in
"$lock")
  $LOCK_CMD
  ;;
"$sleep")
  [[ "$(confirm_action '󰒲  Suspend system?')" == "Yes" ]] && systemctl suspend
  ;;
"$logout")
  if [[ "$(confirm_action '  Logout?')" == "Yes" ]]; then
    if command -v qtile &>/dev/null; then
      qtile cmd-obj -o cmd -f shutdown
    elif command -v i3-msg &>/dev/null; then
      i3-msg exit
    else
      loginctl terminate-session "$XDG_SESSION_ID"
    fi
  fi
  ;;
"$reboot")
  [[ "$(confirm_action '󱑞  Reboot system?')" == "Yes" ]] && systemctl reboot
  ;;
"$shutdown")
  [[ "$(confirm_action '󰐥  Power off system?')" == "Yes" ]] && systemctl poweroff
  ;;
"$cancel" | *)
  exit 0
  ;;
esac
