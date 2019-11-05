import csv
import os
import re

from collections import namedtuple

from aqt.utils import showInfo

# TODO make configurable?
PITCH_RAISE = "["
PITCH_LOWER = "]"
PITCH_STEADY = "-"

DIR_PATH = os.path.dirname(os.path.normpath(__file__))
NHK_DICT = os.path.join(DIR_PATH, "accent_db.csv")

nhk_dict = {}

# taken from nhk-pronunciaton
# annotated myself because I couldn't figure out what
# each of these fields actually meant
AccentEntry = namedtuple('AccentEntry', [
    'NID',            # unique key for each entry
    'ID',             # associates entries with same accent but different midashigo
    'WAVname',
    'K_FLD',
    'ACT',
    'midashigo',      # searchable expression (useful when searching in actual dictionary)
    'nhk',            # standard expression (for words with common kana readings)
    'kanjiexpr',      # kanji expression (forces the kanji reading, often the same as nhk)
    'NHKexpr',
    'numberchars',    # in midashigo1 (and midashigo)
    'nopronouncepos', # 1-indexed, marks some chars as not pronounced in everyday speech
    'nasalsoundpos',  # 1-indexed, marks ga,gi,gu,ge,go with nasal pronunciation
    'majiri',         # example sentence
    'kaisi',          # starting pos in majiri
    'KWAV',
    'midashigo1',     # similar to midashigo, but always in katakana, with long syllables (ー),
                      # and with nasal pronunciation removed
    'akusentosuu',    # number of entries with the same ID
    'bunshou',        # ???
    'ac',             # accent, if shorter than numberchars, have to 0 pad front
                      # 0 = low, 1 = plain (high), 2 = top (next is low)
])

def is_katakana(char):
    return char >= "ァ" and char <= "ヺ"

KATAKANA_TO_HIRAGANA = ord("ぁ") - ord("ァ")
def to_hiragana(char):
    # # ignore ヵ and ヶ which should pretty much always stay in katakana
    if char >= "ァ" and char <= "ヴ":
        return chr(ord(char) + KATAKANA_TO_HIRAGANA)
    else:
        return char

# tenten is the next char in the unicode code block
# not true for う but good enough for what I'm using this for
def add_tenten(char):
    return chr(ord(char)+1)

def correct_hiragana_mixed(key, value):
    i = 0
    # append garbage to key so it has the same length
    key = key + "_"*(len(value)-len(key))
    corrected = ""

    for k, v in zip(key, value):
        if k == v:
            # key includes katakana so fine?
            corrected += v
        else:
            corrected += to_hiragana(v)

    return corrected

# generally mixed words come in two forms:
#  1. start with non-katakana and end with katakana
#  2. start with katakana and end with non-katakana
def correct_hiragana(key, value):
    if is_katakana(key[0]):
        return correct_hiragana_mixed(key, value)
    elif is_katakana(key[-1]):
        return correct_hiragana_mixed(key[::-1], value[::-1])[::-1]
    else:
        return "".join(map(to_hiragana, value))

# pos is a "0" delimeted list of positions
# but it can also hold numbers greater than 9
# which is just stupid as to why they would delimit on "0"...
def correct_pos(pos):
    pos = pos.split("0")

    last = None
    for i, p in enumerate(pos):
        if p:
            pos[i] = int(p)
            last = i
        else:
            pos[last] *= 10

    return [x for x in pos if x]

def correct_nasal(chars, pos):
    if not pos:
        return chars

    pos = correct_pos(pos)

    for p in pos:
        p -= 1
        if p < len(chars):
            chars = chars[:p] + add_tenten(chars[p]) + chars[p+1:]

    return chars

def format_accent(entry):
    chars = entry.midashigo1
    # zero pad the accent
    accents = entry.ac
    accents = "0"*(len(chars)-len(accents))+accents
    # correct the kana
    chars = correct_nasal(chars, entry.nasalsoundpos)
    chars = correct_hiragana(entry.nhk, chars)

    word = ""
    last = "0"
    for char, accent in zip(chars, accents):
        if accent != "0" and last == "0":
            word += PITCH_RAISE
        word += char
        if accent == "2":
            word += PITCH_LOWER
        last = accent

    if last == "1":
        word += PITCH_STEADY

    return word

def build_dict():
    for entry in map(AccentEntry._make, csv.reader(open(NHK_DICT, "r"))):
        value = format_accent(entry)
        for key in [entry.nhk, entry.kanjiexpr]:
            if key in nhk_dict:
                if value not in nhk_dict[key]:
                    nhk_dict[key].append(value)
            else:
                nhk_dict[key] = [value]

def get_pronunciations(text):
    if not nhk_dict:
        build_dict()

    return nhk_dict.get(text, [])
