#!/bin/bash

xset b off

primaryMonitor="eDP1"
secondMonitor="DP1"

if xrandr | grep -q "${secondMonitor} connected"; then
  xrandr --output "${secondMonitor}" --mode "1680x1050" --left-of "${primaryMonitor}"
else
  xrandr --output "${secondMonitor}" --off
fi
