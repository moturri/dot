#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import logging
import re
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.ERROR)
EXECUTOR = ThreadPoolExecutor(max_workers=1)


def execute_audio_command(cmd):
    def _run_cmd():
        try:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    EXECUTOR.submit(_run_cmd)


def vol():
    try:
        out = subprocess.check_output(
            ["amixer", "sget", "Master"],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=0.2,
        )
        vol_match = re.search(r"\[([0-9]+)%\]", out)
        mute_match = re.search(r"\[(on|off)\]", out)

        volume = int(vol_match.group(1)) if vol_match else 0
        muted = mute_match.group(1) == "off" if mute_match else True

        if muted:
            icon, color = "󰖁", "dimgrey"
        elif volume >= 70:
            icon, color = "󰕾", "salmon"
        elif volume >= 40:
            icon, color = "󰖀", "violet"
        elif volume > 0:
            icon, color = "󰕿", "springgreen"
        else:
            icon, color = "󰕿", "palegreen"

        return f'<span foreground="{color}">{icon} {volume:>3}%</span>'
    except Exception:
        return '<span foreground="dimgrey">󰖁  --%</span>'


def mic():
    try:
        out = subprocess.check_output(
            ["amixer", "sget", "Capture"],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=0.2,
        )
        vol_match = re.search(r"\[([0-9]+)%\]", out)
        mute_match = re.search(r"\[(on|off)\]", out)

        volume = int(vol_match.group(1)) if vol_match else 0
        muted = mute_match.group(1) == "off" if mute_match else True

        icon = "󰍭" if muted else "󰍬"
        color = (
            "dimgrey"
            if muted
            else "salmon"
            if volume >= 70
            else "violet"
            if volume >= 40
            else "springgreen"
            if volume > 0
            else "palegreen"
        )

        return f'<span foreground="{color}">{icon} {volume:>3}%</span>'
    except Exception:
        return '<span foreground="dimgrey">󰍭  --%</span>'


def bright():
    try:
        output = subprocess.check_output(
            ["brillo", "-G"], stderr=subprocess.DEVNULL, text=True, timeout=0.2
        )
        percent = int(float(output.strip()))

        if percent >= 80:
            icon, color = "󰃠", "gold"
        elif percent >= 60:
            icon, color = "󰃝", "darkorange"
        elif percent >= 40:
            icon, color = "󰃟", "orchid"
        elif percent >= 20:
            icon, color = "󰃞", "pink"
        else:
            icon, color = "󰃜", "dimgrey"

        return f'<span foreground="{color}">{icon}  {percent:>3}%</span>'
    except Exception:
        return '<span foreground="grey">󰳲  --%</span>'


def batt():
    try:
        with open("/sys/class/power_supply/BAT0/capacity") as f:
            capacity = int(f.read().strip())
        with open("/sys/class/power_supply/AC/online") as f:
            charging = f.read().strip() == "1"

        if capacity >= 80:
            icon, color = "", "lime"
        elif capacity >= 60:
            icon, color = "", "palegreen"
        elif capacity >= 40:
            icon, color = "", "orange"
        elif capacity >= 20:
            icon, color = "", "coral"
        else:
            icon, color = "", "red"

        if charging:
            icon = f" {icon}"
            color = "aqua"

        return f'<span foreground="{color}">{icon}  {capacity:>3}%</span>'
    except Exception:
        return '<span foreground="grey">󰈸  --%</span>'


# --- Volume Controls ---
def volume_up(qtile=None):
    execute_audio_command(["amixer", "-q", "set", "Master", "5%+"])


def volume_down(qtile=None):
    execute_audio_command(["amixer", "-q", "set", "Master", "5%-"])


def volume_mute(qtile=None):
    execute_audio_command(["amixer", "-q", "set", "Master", "toggle"])


# --- Microphone Controls ---
def mic_up(qtile=None):
    execute_audio_command(["amixer", "-q", "set", "Capture", "5%+"])


def mic_down(qtile=None):
    execute_audio_command(["amixer", "-q", "set", "Capture", "5%-"])


def mic_mute(qtile=None):
    execute_audio_command(["amixer", "-q", "set", "Capture", "toggle"])
