#!/usr/bin/env python

import requests, re

listURL = "http://www.couchtuner.la/tv-list/"

shows=["The 100","The Americans","Arrow","Black Mirror","The Blacklist","Blindspot","The Flash","Grimm","Hawaii Five-0","Humans","iZombie","Limitless","Agent Carter","Marvels Agents of Shield","Daredevil","Jessica Jones","Minority Report","Mr. Robot","NCIS","Numb3rs","Orphan Black","Person of Interest","Scandal","Sherlock"]

rList = requests.get(listURL)
textList = rList.text

for show in shows:
    regex = r"<li>((<a (title=\".+\" )?href=\"(?P<link1>.+)\">)(<strong>)|(<strong>)(<a (title=\".+\" )?href=\"(?P<link2>.+)\">))(.*?)" + r"(.*?)".join(show) + r"(.*?)(<[\s\S]*?)<\/li>"
    
    #Check, if the regex is part of the whole source code
    m = re.search(regex, textList, re.IGNORECASE)
    if m:
        if m.group("link1"):
            showURL = m.group("link1")
        elif m.group("link2"):
            showURL = m.group("link2")
        else:
            showURL = 0
    else: 
        showURL = 0
    
    if showURL:
        rShow = requests.get(showURL)
        textShow = rShow.text
        
