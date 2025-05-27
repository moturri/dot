import subprocess
from functools import wraps
from time import monotonic
from typing import Callable, List, Optional


def cached(seconds: int):
    def decorator(func: Callable):
        last_call = {}
        last_result = {}

        @wraps(func)
        def wrapper(*args, force=False, **kwargs):
            now = monotonic()
            if not force and now - last_call.get(func, 0) < seconds:
                return last_result.get(func)
            result = func(*args, **kwargs)
            last_call[func] = now
            last_result[func] = result
            return result

        return wrapper

    return decorator


def fmt(icon: str, val: int, color: str) -> str:
    return f'<span foreground="{color}">{icon}  {val:>3}%</span>'


def run_command(cmd_list: List[str], get_output: bool = False) -> Optional[str]:
    try:
        if get_output:
            return subprocess.check_output(
                cmd_list, text=True, stderr=subprocess.DEVNULL, timeout=1
            ).strip()
        subprocess.run(
            cmd_list,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=1,
            check=True,
        )
        return None
    except (subprocess.SubprocessError, OSError):
        return "" if get_output else None
