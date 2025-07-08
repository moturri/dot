#!/bin/bash

set -euo pipefail

function run() {
  if ! pgrep -f "$1" >/dev/null; then
    "$@" &
  fi
}

xset b off

setxkbmap -option ctrl:nocaps

run greenclip daemon
run /usr/bin/lxqt-policykit-agent
run dunst
run nm-applet
# run picom -b
