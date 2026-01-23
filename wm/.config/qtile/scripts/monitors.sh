#!/bin/sh

# Set the primary display
primary="eDP-1"

# Check for connected displays
hdmi_display="HDMI-1"
dp_display="DP-1"

# Check if HDMI is connected and set it to the left of the primary
if xrandr | grep -q "^$hdmi_display connected"; then
	xrandr --output "$primary" --primary --auto --output "$hdmi_display" --auto --left-of "$primary"

# Check if DisplayPort is connected and set it to the left of the primary
elif xrandr | grep -q "^$dp_display connected"; then
	xrandr --output "$primary" --primary --auto --output "$dp_display" --auto --left-of "$primary"

# If no external display is connected, only use the primary
else
	xrandr --output "$primary" --primary --auto --output "$hdmi_display" --off --output "$dp_display" --off
fi
