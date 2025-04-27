#!/bin/bash

query=$(rofi -dmenu -i -p "󰇥 ")

[ -z "$query" ] && exit

encoded_query=$(printf '%s\n' "$query" | jq -sRr @uri)

engine="https://duckduckgo.com/?q="

xdg-open "${engine}${encoded_query}" >/dev/null 2>&1 &
