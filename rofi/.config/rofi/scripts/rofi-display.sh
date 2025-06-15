#!/usr/bin/env bash
set -euo pipefail

EXTERNAL_DISPLAY="${1:-DP-1}"
INTERNAL_DISPLAY="eDP-1"

connect_display() {
  local position=$1
  xrandr --output "$EXTERNAL_DISPLAY" --auto --"${position}"-of "$INTERNAL_DISPLAY"
  notify-send "Display" "Monitor connected $position of laptop" -t 6000
}

disconnect_display() {
  xrandr --output "$EXTERNAL_DISPLAY" --off
  notify-send "Display" "External monitor disconnected" -t 6000
}

refresh_qtile() {
  sleep 0.5
  # qtile cmd-obj -o cmd -f restart
}

main() {
  action=$(printf '%s\n' "Connect 󰍺" "Disconnect 󰍺" | rofi -dmenu -i -p "󰌢 󱘖 󰍺")
  [[ -z "${action}" ]] && exit 0

  case "$action" in
  "Connect 󰍺")
    position=$(printf '%s\n' left right | rofi -dmenu -i -p "󰌢 󱘖 󰍺 Position")
    [[ -z "${position}" ]] && exit 0
    connect_display "$position"
    # refresh_qtile
    ;;

  "Disconnect 󰍺")
    disconnect_display
    # refresh_qtile
    ;;

  *)
    exit 0
    ;;
  esac
}

main
