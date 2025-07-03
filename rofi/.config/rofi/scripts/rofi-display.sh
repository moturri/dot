#!/usr/bin/env bash

# Compatible with bash and zsh
set -euo pipefail

# Configurable variables
EXTERNAL_DISPLAY="${1:-DP-1}"
INTERNAL_DISPLAY="eDP-1"
ROFI_CMD="rofi -dmenu -i -p"

# Check if external display is connected
if ! xrandr | grep -q "$EXTERNAL_DISPLAY connected"; then
    notify-send "Display" "⚠️ $EXTERNAL_DISPLAY is not connected." -t 5000
    exit 1
fi

# Main menu
main() {
    local options="Auto (Right)\nAuto (Left)\nDisconnect"
    local action
    action=$(echo -e "$options" | $ROFI_CMD "󰌢  ")

    [[ -z "${action}" ]] && exit 0

    case "$action" in
    "Auto (Right)")
        xrandr --output "$EXTERNAL_DISPLAY" --auto --right-of "$INTERNAL_DISPLAY"
        notify-send "Display" "Monitor connected to the right of the laptop." -t 6000
        ;;
    "Auto (Left)")
        xrandr --output "$EXTERNAL_DISPLAY" --auto --left-of "$INTERNAL_DISPLAY"
        notify-send "Display" "Monitor connected to the left of the laptop." -t 6000
        ;;
    "Disconnect")
        xrandr --output "$EXTERNAL_DISPLAY" --off
        notify-send "Display" "External monitor disconnected." -t 6000
        ;;
    *)
        exit 1
        ;;
    esac

    # Optional Qtile refresh
    # sleep 1 && qtile cmd-obj -o cmd -f restart
}

main
