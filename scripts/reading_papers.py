#!/usr/bin/env python3
"""Compatibility CLI for earlier releases; prefer scripts/paper_reading.py."""
from pathlib import Path
import runpy

if __name__ == '__main__':
    runpy.run_path(str(Path(__file__).with_name('paper_reading.py')), run_name='__main__')
