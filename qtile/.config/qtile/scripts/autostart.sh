#!/bin/bash

function run_app() {
  if ! pgrep -f "$1" >/dev/null; then
    "$@" &
  fi
}

run_app greenclip daemon
run_app /usr/bin/lxqt-policykit-agent
run_app dunst
run_app nm-applet
# run_app picom -b
