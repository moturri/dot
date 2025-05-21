import functools
import subprocess
import time


def cached(seconds: float, *, cache_none: bool = False):
    """
    Decorator to cache function output for a set duration.
    """

    def wrap(fn):
        cache = {"value": None, "timestamp": 0.0}

        @functools.wraps(fn)
        def inner(force=False):
            now = time.monotonic()
            if not force and (now - cache["timestamp"]) < seconds:
                return cache["value"]
            out = fn()
            if out is not None or cache_none:
                cache["value"], cache["timestamp"] = out, now
            return out

        return inner

    return wrap


FMT = '<span foreground="{color}">{icon}  {val:>3}%</span>'


def fmt(icon: str, val: int, color: str) -> str:
    return FMT.format(icon=icon, val=val, color=color)


def run_command(cmd_list, get_output=False):
    try:
        if get_output:
            return subprocess.check_output(
                cmd_list,
                text=True,
                stderr=subprocess.DEVNULL,
                timeout=2.5,
            ).strip()
        else:
            subprocess.run(
                cmd_list,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=2.5,
            )
    except Exception:
        return "" if get_output else None

