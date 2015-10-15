#!/usr/bin/env python
# -*- coding: utf-8 -*-

from plugin import Plugin_Base

class Plugin(Plugin_Base):
    def run():
        self.name="Test"
        print("I could do sth now")
        print("Hello Wörld!")

