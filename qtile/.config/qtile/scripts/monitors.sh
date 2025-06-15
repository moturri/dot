#!/bin/bash

primaryMonitor="eDP-1"
secondMonitor="DP-1"

if xrandr | grep -q "${secondMonitor} connected"; then
	xrandr --output "${secondMonitor}" --auto --left-of "${primaryMonitor}"
else
	xrandr --output "${secondMonitor}" --off
fi
