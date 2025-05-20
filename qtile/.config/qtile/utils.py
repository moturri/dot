import functools
import logging
import os
import subprocess
import time
import traceback

logger = logging.getLogger(__name__)


def cached(seconds: float, *, cache_none: bool = False, debug: bool = False):
    """
    Decorator to cache function output for a set duration.
    """
    debug = debug or os.getenv("DEBUG_CACHE") == "1"

    def wrap(fn):
        cache = {"value": None, "timestamp": 0.0}

        @functools.wraps(fn)
        def inner(force=False):
            now = time.monotonic()
            if not force and (now - cache["timestamp"]) < seconds:
                return cache["value"]

            try:
                out = fn()
                if out is not None or cache_none:
                    cache["value"], cache["timestamp"] = out, now
                return out
            except Exception as e:
                if debug:
                    logger.error(
                        f"Error in function '{fn.__name__}': {e}\n{traceback.format_exc()}"
                    )
                return cache["value"]

        return inner

    return wrap


FMT = '<span foreground="{color}">{icon}  {val:>3}%</span>'


def fmt(icon: str, val: int, color: str, _FMT=FMT) -> str:
    """
    Format Qtile widget markup string with color, icon, and value.
    """
    return _FMT.format(icon=icon, val=val, color=color)


def run_command(cmd_list, get_output=False, handle_errors=True):
    """
    Run a system command and optionally capture output.
    """
    try:
        if get_output:
            return subprocess.check_output(
                cmd_list,
                text=True,
                stderr=subprocess.DEVNULL if handle_errors else None,
                timeout=2.5,  # prevent hangs
            ).strip()
        else:
            subprocess.run(
                cmd_list,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=2.5,
            )
            return None
    except Exception as e:
        if handle_errors:
            logger.error("Command error '%s': %s", " ".join(cmd_list), e)
            return "" if get_output else None
        else:
            raise
