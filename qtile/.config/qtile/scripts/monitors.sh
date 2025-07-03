#!/bin/bash

primaryMonitor="eDP-1"
secondMonitor="DP-1"

if xrandr | grep -q "${secondMonitor} connected"; then
	xrandr --output "${primaryMonitor}" --primary --auto --output "${secondMonitor}" --auto --left-of "${primaryMonitor}" || exit 1
else
	xrandr --output "${primaryMonitor}" --primary --auto --output "${secondMonitor}" --off || exit 1
fi
