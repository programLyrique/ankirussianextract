#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Abstract model of a dictionary and a word"""

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

def format_translations(translations):
    """Get a list of translations and return nice html"""
    res=""
    for trans in translations:
        res = res + "<p>" + trans[0] + "</p>\n"
    return res

class Word:
    """A Russian word, with its translations, audio, examples"""
    def __init__(self, normal_form):
        self.normal_form = normal_form
        self.translations = []
        self.audio = None
        self.example = ""

    def gen_note(self):
        """Generate an ANki note for the word"""
        audiotext = ""
        if self.audio is not None:
            audiotext = "[sound:"+ self.audio + "]"
        translations = format_translations(self.translations)
        return genanki.Note(
            model = smodel,
            fields=[self.normal_form, self.examples[0], audiotext, translations]
        )
