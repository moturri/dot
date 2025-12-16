#!/bin/bash

set -euo pipefail

function run() {
	if ! pgrep -f "$1" >/dev/null; then
		"$@" &
	fi
}

run greenclip daemon
run dunst
run /usr/lib/polkit-kde-authentication-agent-1
run nm-applet
run redshift
run xrdb ~/.Xresources
# run picom -b
