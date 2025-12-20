#!/bin/bash

set -euo pipefail

function run() {
	if ! pgrep -f "$1" >/dev/null; then
		"$@" &
	fi
}

run greenclip daemon
run dunst
run /usr/bin/lxqt-policykit-agent
run nm-applet
run redshift
run xrdb ~/.Xresources
# run picom -b
