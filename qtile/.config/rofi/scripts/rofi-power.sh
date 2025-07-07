#!/usr/bin/env bash
set -euo pipefail

LOCK_CMD="${LOCK_CMD:-}"
ROFI_CMD="rofi -dmenu -i -p"

if [[ -z "$LOCK_CMD" ]]; then
  for lock in betterlockscreen i3lock xlock swaylock; do
    if command -v "$lock" >/dev/null 2>&1; then
      LOCK_CMD="$lock"
      break
    fi
  done
fi

lock="󰌾  Lock"
sleep="󰒲  Sleep"
logout="  Logout"
reboot="󱑞  Reboot"
shutdown="󰐥  Shutdown"
cancel="󰜺  Cancel"

options=("$lock" "$sleep" "$logout" "$reboot" "$shutdown" "$cancel")

choice=$(printf '%s\n' "${options[@]}" | $ROFI_CMD "󰟀 Power" -lines "${#options[@]}" || exit 1)

confirm_action() {
  local prompt="$1"
  echo -e "Yes\nNo" | $ROFI_CMD "$prompt"
}

logout_session() {
  if pgrep -x qtile >/dev/null; then
    qtile cmd-obj -o cmd -f logout
  elif pgrep -x i3 >/dev/null; then
    i3-msg exit
  elif [[ -n "${XDG_SESSION_ID:-}" ]]; then
    loginctl terminate-session "$XDG_SESSION_ID"
  else
    loginctl terminate-user "$USER"
  fi
}

case "$choice" in
"$lock")
  if [[ -n "$LOCK_CMD" ]]; then
    exec "$LOCK_CMD"
  else
    notify-send "Power Menu " "No lock command found in PATH."
  fi
  ;;
"$sleep")
  [[ "$(confirm_action '󰒲  Suspend system?')" == "Yes" ]] && systemctl suspend
  ;;
"$logout")
  [[ "$(confirm_action '  Logout?')" == "Yes" ]] && logout_session
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
