#!/bin/bash

function run() {
  if ! pgrep -f "$1" >/dev/null; then
    "$@" &
  fi
}

run greenclip daemon
run /usr/bin/lxqt-policykit-agent
run dunst
run nm-applet
# run_app picom -b
