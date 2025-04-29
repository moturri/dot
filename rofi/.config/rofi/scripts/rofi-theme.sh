#!/bin/bash

declare -A ROFI_THEMES
ROFI_THEMES["Dark"]="dark.rasi"
ROFI_THEMES["Light"]="light.rasi"

SELECTED=$(printf "%s\n" "Dark" "Light" | rofi -dmenu -p "Rofi Theme")

[ -z "$SELECTED" ] && exit 0

ROFI_THEME_FILE="${ROFI_THEMES[$SELECTED]}"
ROFI_THEME_PATH="$HOME/.config/rofi/themes/$ROFI_THEME_FILE"

if [ ! -f "$ROFI_THEME_PATH" ]; then
	notify-send "Theme Error" "The theme file '$ROFI_THEME_FILE' does not exist!"
	exit 1
fi

ROFI_CONFIG="$HOME/.config/rofi/config.rasi"

if grep -q "^@theme" "$ROFI_CONFIG"; then
	sed -i "s|^@theme.*|@theme \"$ROFI_THEME_FILE\"|" "$ROFI_CONFIG"
else
	echo "@theme \"$ROFI_THEME_FILE\"" >>"$ROFI_CONFIG"
fi

notify-send "Rofi Theme Applied" "$ROFI_THEME_FILE"
