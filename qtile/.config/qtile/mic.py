import subprocess
import re
from utils import cached, fmt

def get_current_mic_volume():
    try:
        output = subprocess.check_output("pactl get-source-volume @DEFAULT_SOURCE@", shell=True).decode()
        match = re.search(r"(\d+)%", output)
        return int(match.group(1)) if match else 0
    except Exception:
        return 0

@cached(1)
def mic():
    try:
        output = subprocess.check_output("pactl get-source-volume @DEFAULT_SOURCE@", shell=True).decode()
        mute_status = subprocess.check_output("pactl get-source-mute @DEFAULT_SOURCE@", shell=True).decode()
        match = re.search(r"(\d+)%", output)
        volume = int(match.group(1)) if match else 0
        muted = "yes" in mute_status.lower()
    except Exception:
        return fmt("󰍭", 0, "dimgrey")

    icon = "󰍭" if muted else "󰍬"
    if muted:
        color = "dimgrey"
    elif volume >= 70:
        color = "salmon"
    elif volume >= 40:
        color = "violet"
    elif volume > 0:
        color = "springgreen"
    else:
        color = "palegreen"

    return fmt(icon, volume, color)

def mic_up(qtile=None):
    current = get_current_mic_volume()
    if current < 100:
        increment = min(2, 100 - current)
        subprocess.run(f"pactl set-source-volume @DEFAULT_SOURCE@ +{increment}%", shell=True)
    mic(force=True)

def mic_down(qtile=None):
    subprocess.run("pactl set-source-volume @DEFAULT_SOURCE@ -2%", shell=True)
    mic(force=True)

def mic_mute(qtile=None):
    subprocess.run("pactl set-source-mute @DEFAULT_SOURCE@ toggle", shell=True)
    mic(force=True)


# ------------------------ amixer mic ----------------------------
# def get_current_mic_volume():
#     try:
#         output = subprocess.check_output("amixer get Capture", shell=True).decode()
#         match = re.search(r"\[(\d+)%\]", output)
#         return int(match.group(1)) if match else 0
#     except Exception:
#         return 0
#
#
# @cached(1)
# def mic():
#     try:
#         output = subprocess.check_output("amixer get Capture", shell=True).decode()
#         volume_match = re.search(r"\[(\d+)%\]", output)
#         mute_match = re.search(r"\[(on|off)\]", output)
#         volume = int(volume_match.group(1)) if volume_match else 0
#         muted = mute_match and mute_match.group(1) == "off"
#     except Exception:
#         return fmt("󰍭", 0, "dimgrey")
#
#     icon = "󰍭" if muted else "󰍬"
#     if muted:
#         color = "dimgrey"
#     elif volume >= 70:
#         color = "salmon"
#     elif volume >= 40:
#         color = "violet"
#     elif volume > 0:
#         color = "springgreen"
#     else:
#         color = "palegreen"
#
#     return fmt(icon, volume, color)
#
#
# def mic_up(qtile=None):
#     subprocess.run("amixer set Capture 2%+", shell=True)
#     mic(force=True)
#
#
# def mic_down(qtile=None):
#     subprocess.run("amixer set Capture 2%-", shell=True)
#     mic(force=True)
#
#
# def mic_mute(qtile=None):
#     subprocess.run("amixer set Capture toggle", shell=True)
#     mic(force=True)

# ------------------------- pactl mic ------------------------------
# def get_current_mic_volume():
#     try:
#         output = subprocess.check_output("pactl get-source-volume @DEFAULT_SOURCE@", shell=True).decode()
#         match = re.search(r'(\d+)%', output)
#         return int(match.group(1)) if match else 0
#     except Exception:
#         return 0
#
#
# @cached(1)
# def mic():
#     try:
#         output = subprocess.check_output("pactl get-source-volume @DEFAULT_SOURCE@", shell=True).decode()
#         mute_status = subprocess.check_output("pactl get-source-mute @DEFAULT_SOURCE@", shell=True).decode()
#         match = re.search(r'(\d+)%', output)
#         volume = int(match.group(1)) if match else 0
#         muted = "yes" in mute_status.lower()
#     except Exception:
#         return fmt("󰍭", 0, "dimgrey")
#
#     icon = "󰍭" if muted else "󰍬"
#     if muted:
#         color = "dimgrey"
#     elif volume >= 70:
#         color = "salmon"
#     elif volume >= 40:
#         color = "violet"
#     elif volume > 0:
#         color = "springgreen"
#     else:
#         color = "palegreen"
#
#     return fmt(icon, volume, color)
#
#
# def mic_up(qtile=None):
#     current = get_current_mic_volume()
#     if current < 100:
#         increment = min(2, 100 - current)
#         subprocess.run(f"pactl set-source-volume @DEFAULT_SOURCE@ +{increment}%", shell=True)
#     mic(force=True)
#
#
# def mic_down(qtile=None):
#     subprocess.run("pactl set-source-volume @DEFAULT_SOURCE@ -2%", shell=True)
#     mic(force=True)
#
#
# def mic_mute(qtile=None):
#     subprocess.run("pactl set-source-mute @DEFAULT_SOURCE@ toggle", shell=True)
#     mic(force=True)
