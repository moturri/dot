#!/bin/sh

primary="eDP-1"
secondary="DP-1"

if xrandr | grep -q "^$secondary connected"; then
	xrandr --output "$primary" --primary --auto \
		--output "$secondary" --auto --left-of "$primary"
else
	xrandr --output "$primary" --primary --auto \
		--output "$secondary" --off
fi
