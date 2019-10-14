Anki Russian Extract
======================

Takes subtitles and extract normalized words by frequency with example to create an Anki desk.
For now dedicated to Russian words and Russin subtitles.

## Supported subtitles:

- Webvt: .vtt
- SubRip: .srt
- SubStationAlpha: .ass, .ssa
- MicroDVD: .sub
- MPL2: .txt 
- TMP Player
- json serialized

# Dependencies

- pysubs2
- webvtt
- pystardict
- genanki

To install dependencies, just do:

```
pip install dependency
```

Assumes python3


# Dictionnaries

Assumes dictionaries with Lingvo format. You can find Russian -> Frenc, and Russian -> English dictionnaries [here](http://download.huzheng.org/lingvo/)

# Usage

```
positional arguments:
  S              a subtitle file

optional arguments:
  -h, --help     show this help message and exit
  --words WORDS  Dictionnary of known words
  --dict DICT    Dictionnary for translations
```
