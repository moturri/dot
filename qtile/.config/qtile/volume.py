import subprocess
import re
from utils import cached, fmt


def get_current_volume():
    try:
        output = subprocess.check_output(
            "pactl get-sink-volume @DEFAULT_SINK@", shell=True
        ).decode()
        match = re.search(r"(\d+)%", output)
        return int(match.group(1)) if match else 0
    except Exception:
        return 0


@cached(10)
def vol():
    try:
        output = subprocess.check_output(
            "pactl get-sink-volume @DEFAULT_SINK@", shell=True
        ).decode()
        mute_status = subprocess.check_output(
            "pactl get-sink-mute @DEFAULT_SINK@", shell=True
        ).decode()
        match = re.search(r"(\d+)%", output)
        volume = int(match.group(1)) if match else 0
        muted = "yes" in mute_status.lower()
    except Exception:
        return fmt("󰖁", 0, "dimgrey")

    if muted:
        return fmt("󰝟", volume, "dimgrey")
    elif volume >= 70:
        return fmt("󰕾", volume, "salmon")
    elif volume >= 40:
        return fmt("󰖀", volume, "orchid")
    elif volume > 0:
        return fmt("󰕿", volume, "springgreen")
    else:
        return fmt("󰕿", volume, "palegreen")


def vol_up(qtile=None):
    current = get_current_volume()
    if current < 100:
        increment = min(2, 100 - current)
        subprocess.run(
            f"pactl set-sink-volume @DEFAULT_SINK@ +{increment}%", shell=True
        )
    vol(force=True)


def vol_down(qtile=None):
    subprocess.run("pactl set-sink-volume @DEFAULT_SINK@ -2%", shell=True)
    vol(force=True)


def vol_mute(qtile=None):
    subprocess.run("pactl set-sink-mute @DEFAULT_SINK@ toggle", shell=True)
    vol(force=True)
