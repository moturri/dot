#!/bin/bash

query=$(rofi -dmenu -i -p "󰇥 ")

[ -z "$query" ] && exit 0

encoded_query=$(printf '%s\n' "$query" | jq -sRr @uri)

xdg-open "https://duckduckgo.com/?q=${encoded_query}" >/dev/null 2>&1 &
