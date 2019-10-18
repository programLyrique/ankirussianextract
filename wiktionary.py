#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Extract words from a dump of the English wiktionary with wiktexract (https://github.com/tatuylonen/wiktextract)

wiktwords data/enwiktionary-latest-pages-articles.xml.bz2 --out russiandicts.words --language Russian --translations --pronunciation --statistics

Then extract all the words in the .words file (one json per line).
Then gets the audio of the words with it and download it if not already there.

TODO: convert that to a Python class?

"""

import json
import itertools
import requests
from bs4 import BeautifulSoup
from pathlib import Path

baseURL = "https://commons.wikimedia.org/w/index.php"

def load_dict(dictname):
    """One json per line"""
    with open(dictname, "r") as f:
        rdict = dict()
        for line in f:
            res = json.loads(line)
            rdict[res["word"]] = res
        return rdict

def translate(dico, word):
    """Returns a list of meanings"""
    jsonblob =  dico.get(word) # We actually want None if it's not in the dico
    try:
        if jsonblob is not None:
            return [sense['glosses'] for sense in jsonblob['senses'] ]
        else:
            return []
    except:
        return []

def format_translations(translations):
    """Get a list of translations and return nice html"""
    res=""
    for trans in translations:
        res = res + "<p>" + trans[0] + "</p>\n"
    return res

def mediafilename(dico, word):
    """Get the name of the audio pronunciation file"""
    try:
        # Not always the right order in the last array
        audioarray = None
        for it in dico[word]["pronunciations"]:
            if "audios" in it:
                audioarray =  it["audios"][0]
        # So we crudely search for an ogg file
        return next((x for x in audioarray if ".ogg" in x), None)
    except:
        return None

def get_medias_url(filename):
    """Find the audio url in wikimedia commons. It has the class internal.
    Seems there is always only one internal one?"""
    r = requests.get(baseURL, params={'title' : "File:"+filename})
    html = BeautifulSoup(r.text, 'lxml')
    urls = html.find_all("a", "internal")
    #return [url.get('href') for url in urls]# There should be only one audio file anyway
    return urls[0].get('href')

def download_file(url, path):
    """Write the ogg file"""
    r = requests.get(url)
    with path.open("wb") as f:
        f.write(r.content)
    return r.status_code == requests.codes.ok

def get_audio(filename, dir):
    """Check if file is already there. If not, download it"""
    p = Path(dir, filename)
    if not p.exists():
        try:
            return download_file(get_medias_url(filename), p)
        except:
            print("Connot download and save ", filename)
            return False
    else:
        return True
