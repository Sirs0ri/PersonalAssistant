"""Samantha's main module."""

import sys
from os.path import abspath, dirname

sys.path.insert(0, abspath(dirname('__file__')))

import samantha

__version__ = "1.0.0a1"

samantha.run()