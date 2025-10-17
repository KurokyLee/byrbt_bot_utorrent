import time

def _first_attr(obj, names, default=0):
    for n in names:
        if hasattr(obj, n):
            v = getattr(obj, n)
            if v is not None:
                return v
    return default

def _fmt_bytes(n):
    try:
        n = float(n)
    except Exception:
        n = 0.0
    units = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']
    i = 0
    while n >= 1024 and i < len(units) - 1:
        n /= 1024.0
        i += 1
    return f'{n:.2f}{units[i]}'

def _fmt_speed(n):
    try:
        n = float(n)
    except Exception:
        n = 0.0
    units = ['B/s', 'KiB/s', 'MiB/s', 'GiB/s', 'TiB/s']
    i = 0
    while n >= 1024 and i < len(units) - 1:
        n /= 1024.0
        i += 1
    return f'{n:.2f}{units[i]}'

def _fmt_time(ts):
    if not ts:
        return '-'
    try:
        ts = float(ts)
        if ts > 1e12:
            ts = ts / 1000.0
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))
    except Exception:
        return '-'