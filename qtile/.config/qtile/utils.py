import functools
import time
import traceback


def cached(seconds: float):
    """
    Decorator that caches the return value of a function for a given number of seconds.
    Useful for reducing CPU usage by limiting how often expensive functions are called.
    """

    def wrap(fn):
        cache = [None, 0.0]  # [cached_value, last_updated_time]

        @functools.wraps(fn)
        def inner(force=False):
            now = time.monotonic()
            if not force and cache[0] is not None and (now - cache[1]) < seconds:
                return cache[0]
            try:
                out = fn()
                if out is not None:
                    cache[0], cache[1] = out, now
            except Exception:
                print(f"[cached] Error in '{fn.__name__}':\n{traceback.format_exc()}")
                return cache[0]
            return out if out is not None else cache[0]

        return inner

    return wrap


# Format string for consistent widget output
_FMT = '<span foreground="{color}">{icon}  {val:>3}%</span>'


def fmt(icon: str, val: int, color: str) -> str:
    """
    Format a widget string with color, icon, and value.
    Compatible with Qtile's widget markup (like TextBox with markup=True).
    """
    return _FMT.format(icon=icon, val=val, color=color)
