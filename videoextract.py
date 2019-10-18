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
import genanki
import wiktionary as wiki

# To remove punctuation
table = str.maketrans(dict.fromkeys(string.punctuation))

# Morphological analyzer
morph = pymorphy2.MorphAnalyzer()

# Dictionnaries
dictRusFrench = pyd.Dictionary("stardict-lingvo-RF-Essential-2.4.2/RF-Essential")
dictRusEnglish = pyd.Dictionary("stardict-lingvo-RE-Essential-2.4.2/RE-Essential")
dictRusEnglishLarge = pyd.Dictionary("stardict-rus_eng_full-2.4.2/rus_eng_full")

dictRusEnglishWiki = wiki.load_dict("wiktionary/russiandict.words")
mediadir = "medias"


def translation_from_stardict(line):
    xml = "<root>"+line+"</root>"
    root = ET.fromstring(xml)
    translationNode = root.find("dtrn")
    if translationNode != None:
        return translationNode.text

def translation_fallback(line):
    """The Russian English dic is much less structured"""
    xml = "<root>"+line+"</root>"
    root = ET.fromstring(xml)
    transla = list(root.itertext())
    return transla[1]

def translate(word):
    if dictRusFrench.has_key(word):
        return translation_from_stardict(dictRusFrench[word])
    elif dictRusEnglish.has_key(word):
        return translation_from_stardict(dictRusEnglish[word])
    elif dictRusEnglishLarge.has_key(word):
        return translation_fallback(dictRusEnglishLarge[word].replace("\n", ""))

# Anki stuff
smodel = genanki.Model(
    1897425995,
    "Russian -> French",
    fields=[
    {'name': 'Question'},
    {'name': "Example"},
    {'name': "Media"},
    {'name': 'Answer'},
  ],
  templates=[
    {
      'name': 'Card 1',
      'qfmt': '<div class="ques">{{Question}}</div></br>{{Media}}</br><div class="example">{{Example}}</div>',
      'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
    },
  ],
  css="""
    .card {text-align:center;}
    .ques  {font-weight: bold;}
    /*.example  {font-style: italic;}*/
  """
)

rmodel = genanki.Model(
    1710758133,
    "French -> Russian",
    fields=[
    {'name': 'Question'},
    {'name': "Example"},
    {'name': 'Answer'},
  ],
  templates=[
    {
      'name': 'Card 1',
      'qfmt': '<div class="ques">{{Question}}</div>',
      'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}</br><div class="example">{{Example}}</div>',
    },
  ],
  css="""
    .card {text-align:center;}
    .ques {font-weight: bold;}
    .example {font-style: italic;}
  """
)

def gen_note(word, translation, contextSentence, audio):
    audiotext = ""
    if audio is not None:
        audiotext = "[sound:"+ audio + "]"
    return genanki.Note(
        model = smodel,
        fields=[word, contextSentence, audiotext, translation]
    )

def gen_dek(title, words, translations, contextSentences, audios):
    """Insert Note by frequency"""
    deck = genanki.Deck(1778812731, title)
    for (word,_) in sorted(words.items(), key=operator.itemgetter(1), reverse=True):
        if translations[word] is not None:
            deck.add_note(gen_note(word, translations[word], contextSentences[word], audios[word]))
    return deck

def add_new_words(knownWordFile, words):
    """Add new words to the known words file"""
    with open(knownWordFile, "a") as file:
        for word in words.keys():
            file.write(word + "\n")


def process_subtitle(subfile, knownWordsFile):
    extension = pathlib.Path(subfile).suffix

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
    audios=dict()
    #Keep a sentence with the word in context
    # Only keep the longest one
    contextSentences=dict()
    for sub in subs:
        # Remove punctuation
        line = sub.text.translate(table)
        # Tokenize
        tokens = line.split()
        for token in tokens:
            tok = token.lower()
            #normalize
            normal_form = morph.parse(tok)[0].normal_form
            # Only keep it if we do not it yet
            if normal_form not in knownWords:
                words[normal_form] = words.get(normal_form, 1) + 1
                if normal_form not in translations:
                    #translations[normal_form] = translate(normal_form)#With stardict dictionaries
                    # Now translating with wiktionary
                    transl = wiki.translate(dictRusEnglishWiki, normal_form)
                    if transl != []:
                        translations[normal_form] = wiki.format_translations(transl)
                        if normal_form not in audios:
                            mediafile = wiki.mediafilename(dictRusEnglishWiki, normal_form)
                            if mediafile is not None and wiki.get_audio(mediafile, mediadir):
                                audios[normal_form] = mediafile
                            else:
                                audios[normal_form] = None
                                print("Normal form: ", normal_form)
                    else:
                        translations[normal_form] = None
                # Add an example sentence of needed
                currentExample = contextSentences.get(normal_form, "")
                currentExampleLength = len(currentExample.translate(table).split())
                if  len(tokens) > currentExampleLength:
                    contextSentences[normal_form] = sub.text


    #print(sorted(words.items(), key=operator.itemgetter(1), reverse=True))
    return (words, translations, contextSentences, audios)


# Command line
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate an Anki deck with the most frequent words.')
    parser.add_argument('subfile', metavar='S',  help='a subtitle file')
    parser.add_argument('--words', help='Dictionnary of known words')
    parser.add_argument('--dict', help='Dictionnary for translations')
    args = parser.parse_args()

    # Dictionnary of known words
    knownWordsFile = "knownWords.txt"
    if args.words:
        knownWordsFile = args.words

    print("Processing subtitles ", args.subfile)
    words, translations, contextSentences, audios = process_subtitle(args.subfile, knownWordsFile)
    #print(words)
    #print(translations)
    print("New words: ", len(words), " with ", len(translations), " translations")
    title = pathlib.Path(args.subfile).stem
    print("Generate deck")
    deck =gen_dek(title, words, translations, contextSentences, audios)
    print("Save deck")
    package = genanki.Package(deck)
    package.media_files = [mediadir + "/" + medianame for medianame in audios.values() if medianame is not None]
    package.write_to_file(pathlib.Path(args.subfile).with_suffix(".apkg"))
    print("Updating known words with new words")
    add_new_words(knownWordsFile, words)
