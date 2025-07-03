#!/usr/bin/env bash
# Compatible with Bash and Zsh

# === Safe Mode ===
set -euo pipefail

# === Config ===
SESSION="${1:-m}"
WIFI_INTERFACE="wlan0"
DEFAULT_PROFILE="default"

# === Environment Setup ===
PROFILE="${2:-$DEFAULT_PROFILE}"
ENV_FILE="$HOME/.config/create_ap/env_$PROFILE"

# === Check if env file exists ===
if [[ ! -f "$ENV_FILE" ]]; then
  notify-send "Missing Profile" "Could not find env file:\n$ENV_FILE"
  exit 1
fi

# shellcheck disable=SC1090
. "$ENV_FILE"

# === Functions ===

get_channel() {
  iw dev "$WIFI_INTERFACE" info 2>/dev/null | grep -oE 'channel [0-9]+' | awk '{print $2}' || true
}

notify_err() {
  notify-send "AP Error" "$1"
  exit 1
}

create_ap_tmux() {
  local channel
  channel=$(get_channel)

  if [[ -z "$channel" ]]; then
    notify_err "Wi-Fi channel not found on $WIFI_INTERFACE."
  fi

  # Start tmux session if not already running
  if ! tmux has-session -t "$SESSION" 2>/dev/null; then
    tmux new-session -d -s "$SESSION"
  fi

  # Start create_ap in a new window
  tmux new-window -t "$SESSION:" -n "create_ap" \
    "sudo create_ap '$WIFI_INTERFACE' '$WIFI_INTERFACE' '$SSID' '$PASSWORD' -c $channel; read -n1 -r -p 'Press any key to exit...'"

  tmux attach-session -t "$SESSION"
}

main() {
  local options="Create Hotspot\nAttach to Session"
  local action
  action=$(echo -e "$options" | rofi -dmenu -i -p "create_ap")

  case "$action" in
  "Create Hotspot")
    create_ap_tmux
    ;;
  "Attach to Session")
    tmux attach-session -t "$SESSION" || notify_err "No tmux session '$SESSION' found."
    ;;
  esac
}

main
