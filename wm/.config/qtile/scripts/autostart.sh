#!/bin/bash

set -euo pipefail

# Run a command only if it's not already running
function run() {
	# Check for exact process name match
	if ! pgrep -x "$1" >/dev/null; then
		# Execute all arguments in the background
		"$@" &
	fi
}

# Load X resources
xrdb ~/.Xresources &

# Start daemons and applets
run greenclip daemon
run dunst
run lxqt-policykit-agent
run nm-applet
run redshift
run picom
