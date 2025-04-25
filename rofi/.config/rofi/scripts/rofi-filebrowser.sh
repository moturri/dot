#!/bin/bash

dir="${1:-$HOME}"

while true; do
	selection=$(find "$dir" -maxdepth 1 -mindepth 1 | sort | rofi -dmenu -p "📂 $dir")

	[[ -z "$selection" ]] && exit

	if [[ -d "$selection" ]]; then
		dir="$selection"
	else
		xdg-open "$selection"
		exit
	fi
done
