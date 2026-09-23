"""Re-import our own modules after a deploy.

Streamlit Cloud applies a push by pulling files into the running process. Page
scripts are re-read on every run, but the modules they import (components,
services, models, state) stay cached in sys.modules unless a live session's
file watcher evicts them, and with nobody connected at deploy time nothing
does. A push that adds a name to theme.py and imports it in app.py then fails
with ImportError until a reboot (happened 2026-09-23).

Every page calls refresh() before its own imports: when any of our source files
changed since the last check, our cached modules are dropped so they re-import
from disk. This file itself is not reloaded, so keep it boring.
"""

import os
import sys

_APP_DIR = os.path.dirname(os.path.abspath(__file__))
_WATCHED = (
    os.path.join(_APP_DIR, "components"),
    os.path.join(_APP_DIR, "services"),
    os.path.join(_APP_DIR, "state.py"),
    os.path.join(os.path.dirname(_APP_DIR), "models"),
)
_LOCAL_PACKAGES = {"components", "services", "models", "state"}


def _newest_mtime() -> float:
    newest = 0.0
    for path in _WATCHED:
        if os.path.isfile(path):
            newest = max(newest, os.path.getmtime(path))
            continue
        for root, _, files in os.walk(path):
            for name in files:
                if name.endswith(".py"):
                    newest = max(newest, os.path.getmtime(os.path.join(root, name)))
    return newest


# Baseline at first import, so a fresh process doesn't purge what it just loaded.
_last_seen = _newest_mtime()


def refresh() -> None:
    # ponytail: concurrent sessions share sys.modules; a purge mid-import in
    # another thread is possible but only in the seconds after a deploy.
    global _last_seen
    stamp = _newest_mtime()
    if stamp == _last_seen:
        return
    for name in [m for m in sys.modules if m.split(".")[0] in _LOCAL_PACKAGES]:
        del sys.modules[name]
    _last_seen = stamp
