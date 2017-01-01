"""Samantha's main module."""

import sys
from os.path import abspath, dirname

sys.path.insert(0, abspath(dirname('__file__')))

import samantha

__version__ = "1.0.0a2"


debug = False
force_master = False

if "--debug" in sys.argv or "-D" in sys.argv:
    debug = True
if "--force_master" in sys.argv or "-M" in sys.argv:
    force_master = True
    
    
samantha.run(debug, force_master)