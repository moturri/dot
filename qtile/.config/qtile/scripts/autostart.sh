#!/bin/bash

set -euo pipefail

function run() {
  if ! pgrep -f "$1" >/dev/null; then
    "$@" &
  fi
}

# Disable system bell
xset b off

# Remap Caps Lock to Ctrl (X session only)
setxkbmap -option ctrl:nocaps

# Start apps
run greenclip daemon
run /usr/bin/lxqt-policykit-agent
run dunst
run nm-applet
# run picom -b
