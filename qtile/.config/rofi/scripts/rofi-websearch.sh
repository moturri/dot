#!/usr/bin/env bash
set -euo pipefail

SEARCH_ENGINE_URL="${SEARCH_ENGINE_URL:-https://duckduckgo.com/?q=}"
DEPENDENCIES=(rofi jq xdg-open notify-send)

for cmd in "${DEPENDENCIES[@]}"; do
  command -v "$cmd" >/dev/null 2>&1 || {
    notify-send "Missing Dependency" "❌ $cmd is not installed."
    exit 1
  }
done

query=$(rofi -dmenu -i -p "󰇥 Search" || true)
[[ -z "${query// /}" ]] && exit 0

encoded_query=$(printf '%s' "$query" | jq -sRr @uri)
xdg-open "${SEARCH_ENGINE_URL}${encoded_query}" >/dev/null 2>&1 &
