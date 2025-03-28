#!/bin/bash

#xinput set-prop 11 "libinput Tapping Enabled" 1
# xinput set-prop 11 "libinput Accel Speed" 0.5
# xinput set-prop 11 "libinput Disable While Typing Enabled" 1

xset b off

primaryMonitor="eDP1"
secondMonitor="DP1"

if xrandr | grep -q "${secondMonitor} connected"; then
    xrandr --output "${secondMonitor}" --mode "1680x1050" --left-of "${primaryMonitor}"
else
    xrandr --output "${secondMonitor}" --off
fi

