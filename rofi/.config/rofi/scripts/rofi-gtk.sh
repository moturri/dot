#!/bin/bash

export DISPLAY=:0
export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$(id -u)/bus"

THEMES=(FlatDark FlatLight)

SELECTED=$(printf "%s\n" "${THEMES[@]}" | rofi -dmenu -p "Select GTK Theme")

[ -z "$SELECTED" ] && exit 0

[ -f ~/.gtkrc-2.0 ] && sed -i "s/^gtk-theme-name=.*/gtk-theme-name=\"$SELECTED\"/" ~/.gtkrc-2.0
[ -f ~/.config/gtk-3.0/settings.ini ] && sed -i "2s|.*|gtk-theme-name=$SELECTED|" ~/.config/gtk-3.0/settings.ini
[ -f ~/.config/gtk-4.0/settings.ini ] && sed -i "3s|.*|gtk-theme-name=$SELECTED|" ~/.config/gtk-4.0/settings.ini

notify-send "GTK Theme Applied" "$SELECTED"
