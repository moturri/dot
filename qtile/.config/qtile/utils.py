import functools
import time


def cached(seconds):
    def wrap(fn):
        cache = [None, 0.0]

        @functools.wraps(fn)
        def inner(force=False):
            now = time.monotonic()
            if not force and cache[0] is not None and now - cache[1] < seconds:
                return cache[0]
            try:
                out = fn()
                if out is not None:
                    cache[0], cache[1] = out, now
            except Exception as e:
                print(f"Error executing function {fn.__name__}: {e}")
                return cache[0]
            return out if out is not None else cache[0]

        return inner

    return wrap


_FMT = '<span foreground="{}">{}  {:>3}%</span>'


def fmt(icon: str, val: int, color: str) -> str:
    return _FMT.format(color, icon, val)
