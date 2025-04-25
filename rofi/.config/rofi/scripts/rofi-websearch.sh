#!/bin/bash

query=$(rofi -dmenu -i -p "Search the web:")

[ -z "$query" ] && exit

encoded_query=$(printf '%s\n' "$query" | jq -sRr @uri)

engine="https://duckduckgo.com/?q="

xdg-open "${engine}${encoded_query}" >/dev/null 2>&1 &
