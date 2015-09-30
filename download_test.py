#!/usr/bin/env python

import requests, re

url = "http://www.couchtuner.la/tv-list/"

shows=["The 100","The Americans","Arrow","Black Mirror","The Blacklist","Blindspot","The Flash","Grimm","Hawaii Five-0","Humans","iZombie","Limitless","Agent Carter","Agents of Shield","Daredevil","Jessica Jones","Minority Report","Mr. Robot","NCIS","Numb3rs","Orphan Black","Person of Interest","Scandal","Sherlock"]

r = requests.get(url)
text = r.text

for show in shows:
    m = re.search(r"<li>((<a (title=\".+\" )?href=\"(?P<link1>.+)\">)(<strong>)|(<strong>)(<a (title=\".+\" )?href=\"(?P<link2>.+)\">))(?P<name>{name})(<[\s\S]*?)<\/li>".format(name=show), text)
    if m:
        name = m.group("name")
        if m.group("link1"):
            link = m.group("link1")
        elif m.group("link2"):
            link = m.group("link2")
        print("{0}: {1}".format(name,link))
