#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
- Extract subtitles
- Find out most common words
- Only keep the ones which are not already in a dictionnary of known words
- Generate an Anki deck to review them
"""
import string
import argparse
import pathlib
import pysubs2
import webvtt
import pymorphy2
import operator
import pystardict  as pyd
import xml.etree.ElementTree as ET

# To remove punctuation
table = str.maketrans(dict.fromkeys(string.punctuation))

# Morphological analyzer
morph = pymorphy2.MorphAnalyzer()

# Dictionnaries
dictRusFrench = pyd.Dictionary("stardict-lingvo-RF-Essential-2.4.2/RF-Essential")
dictRusEnglish = pyd.Dictionary("stardict-lingvo-RE-Essential-2.4.2/RE-Essential")
dictRusEnglishLarge = pyd.Dictionary("stardict-rus_eng_full-2.4.2/rus_eng_full")


def translation_from_stardict(line):
    xml = "<root>"+line+"</root>"
    root = ET.fromstring(xml)
    translationNode = root.find("dtrn")
    if translationNode != None:
        return translationNode.text
    else:
        return "X"

def translation_fallback(line):
    """The Russian English dic is much less structured"""
    xml = "<root>"+line+"</root>"
    root = ET.fromstring(xml)
    transla = list(root.itertext())
    if len(transla) == 2:
        return transla[1]
    else:
        return "X"

def translate(word):
    if dictRusFrench.has_key(word):
        return translation_from_stardict(dictRusFrench[word])
    elif dictRusEnglish.has_key(word):
        return translation_from_stardict(dictRusEnglish[word])
    elif dictRusEnglishLarge.has_key(word):
        return translation_fallback(dictRusEnglishLarge[word].replace("\n", ""))
    else:
        return "X"



def process_subtitle(subfile, words):
    extension = pathlib.Path(subfile).suffix

    # Dictionnary of known words
    knownWordsFile = "knownWords.txt"
    if words:
        knownWordsFile = words
    # Load it in memory
    knownWords = set()
    for line in open(knownWordsFile, "r"):
        knownWords.add(line.strip())

    #Load subtitles
    subs=[]
    if extension == ".vtt":
        subs = webvtt.read(subfile)
    else:
        subs = SSAFile.load(subfile)
    # Subs
    words = dict()
    translations=dict()
    for sub in subs:
        # Remove punctuation
        line = sub.text.translate(table)
        # Tokenize
        tokens = line.split()
        for token in tokens:
            tok = token.lower()
            #normalize
            normal_form = morph.parse(tok)[0].normal_form
            if normal_form not in translations:
                translations[normal_form] = translate(normal_form)
            # Only keep it if we do not it yet
            if normal_form not in knownWords:
                words[normal_form] = words.get(normal_form, 1) + 1


    #print(sorted(words.items(), key=operator.itemgetter(1), reverse=True))
    return (words, translations)


# Command line
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate an Anki deck with the most frequent words.')
    parser.add_argument('subfile', metavar='S',  help='a subtitle file')
    parser.add_argument('--words', help='Dictionnary of known words')
    parser.add_argument('--dict', help='Dictionnary for translations')
    args = parser.parse_args()

    words, translations = process_subtitle(args.subfile, args.words)
    print(words)
    print(translations)
