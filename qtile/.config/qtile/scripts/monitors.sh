#!/bin/bash

primaryMonitor="eDP-1"
secondMonitor="DP-1"

if xrandr | grep -q "${secondMonitor} connected"; then
	xrandr --output "${secondMonitor}" --auto --left-of "${primaryMonitor}" || exit 1
else
	xrandr --output "${secondMonitor}" --off || exit 1
fi
