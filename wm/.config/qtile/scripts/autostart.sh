#!/bin/bash

set -euo pipefail

function run() {
	if ! pgrep -x "$1" >/dev/null; then
		"$@" &
	fi
}

# Load X resources
xrdb ~/.Xresources &

# X / GTK settings
run xsettingsd

# Start daemons and applets
run greenclip daemon
run dunst
run lxqt-policykit-agent
run nm-applet
run redshift
# run picom
