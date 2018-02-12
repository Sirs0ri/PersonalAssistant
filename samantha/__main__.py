"""Samantha's main module.

Calling this via 'python samantha' starts everything else."""

import sys
from os.path import abspath, dirname

sys.path.insert(0, abspath(dirname('__file__')))

import samantha

__version__ = "1.6.0"

if "--debug" in sys.argv or "-D" in sys.argv:
    DEBUG = True
else:
    DEBUG = False

plugin_filter = None

if "--plugins" in sys.argv:
    value_index = sys.argv.index("--plugins") + 1
    if len(sys.argv) > value_index:
        plugin_filter = sys.argv[value_index]

if "-P" in sys.argv:
    value_index = sys.argv.index("-P") + 1
    if len(sys.argv) > value_index:
        plugin_filter = sys.argv[value_index]

samantha.run(DEBUG, plugin_filter)
