import functools
import logging
import os
import time
import traceback

# Setup logging for caching
logger = logging.getLogger(__name__)


def cached(seconds: float, *, cache_none: bool = False, debug: bool = False):
    """
    Decorator that caches the return value of a function for a given number of seconds.

    Args:
        seconds (float): How long (in seconds) to cache the result.
        cache_none (bool): If True, cache None values as valid results.
        debug (bool): If True, prints exceptions to stdout (default is False).
                      You can also enable via env var DEBUG_CACHE=1.

    Returns:
        A wrapped function with caching behavior.
    """

    # Enable debug logging from environment variable if set
    debug = debug or os.getenv("DEBUG_CACHE") == "1"

    def wrap(fn):
        cache = [None, 0.0]  # [cached_value, last_updated_time]

        @functools.wraps(fn)
        def inner(force=False):
            now = time.monotonic()

            # Use cache if still valid and not forced
            if not force and (now - cache[1]) < seconds:
                return cache[0]

            try:
                out = fn()

                # Always cache unless it's None and caching None is disabled
                if out is not None or cache_none:
                    cache[0], cache[1] = out, now
                return out

            except Exception as e:
                if debug:
                    logger.error(
                        f"Error in function '{fn.__name__}': {e}\n{traceback.format_exc()}"
                    )
                return cache[0]  # Fall back to last good value

        return inner

    return wrap


# Format string for consistent widget output (Qtile markup)
FMT = '<span foreground="{color}">{icon}  {val:>3}%</span>'


def fmt(icon: str, val: int, color: str) -> str:
    """
    Format a widget string with Qtile markup (span with color, icon, and value).

    Args:
        icon (str): The icon character or string (e.g., Font Awesome symbol).
        val (int): The numeric value to display (e.g., 73 for 73%).
        color (str): The foreground color for the widget (name or hex code).

    Returns:
        str: Markup-formatted string for Qtile widgets.
    """
    return FMT.format(icon=icon, val=val, color=color)
