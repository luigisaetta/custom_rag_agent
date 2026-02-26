"""
File name: tests/conftest.py
Author: Luigi Saetta
Last modified: 25-02-2026
Python Version: 3.11
License: MIT
Description: Pytest shared setup that makes the project root importable during test runs.
"""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
