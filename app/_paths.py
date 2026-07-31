"""_paths.py — import path bootstrap for the Streamlit entry points.

Streamlit puts the main script's folder (``app/``) on ``sys.path`` before it
runs anything, which is how ``components``, ``services``, and ``state`` resolve
from every page. ``models/`` and ``data/`` sit one level above that, so each
entry point imports this module first to make the repository root importable
too.

Tests don't go through Streamlit — they get the same two directories from the
``pythonpath`` setting in ``pyproject.toml``.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
