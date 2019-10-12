import csv
import os
import re

from collections import namedtuple

PITCH_RAISE = "["
PITCH_LOWER = "]"
PITCH_STEADY = "-"

DIR_PATH = os.path.dirname(os.path.normpath(__file__))
NHK_PATH = os.path.normpath(os.path.join(DIR_PATH, "..", "..", "932119536"))
NHK_DICT = os.path.join(NHK_PATH, "ACCDB_unicode.csv")

nhk_dict = {}

AccentEntry = namedtuple('AccentEntry', [
    'NID', # unique key for each entry
    'ID', # associates different keys for same pronunciation
    'WAVname',
    'K_FLD',
    'ACT',
    'midashigo', # searchable expressions (not important? not searching by reading)
    'nhk', # standard expression (for words with common kana readings)
    'kanjiexpr', # kanji reading (for words with common kana readings)
    'NHKexpr',
    'numberchars', # in midashigo1
    'nopronouncepos',
    'nasalsoundpos',
    'majiri', # example sentence
    'kaisi', # starting pos in majiri
    'KWAV',
    'midashigo1', # pronunciation display (in katakana)
    'akusentosuu', # number of accents (relates other entries)
    'bunshou', # ???
    'ac', # accent, if shorter than numchars, have to 0 pad front
])

def is_katakana(char):
    return bool(re.search("[ァ-ヴヷ-ヺ]", char))

KATAKANA_TO_HIRAGANA = ord("ぁ") - ord("ァ")
def to_hiragana(value):
    if value >= "ァ" and value <= "ヴ":
        return chr(ord(value) + KATAKANA_TO_HIRAGANA)
    else:
        return value

def correct_hiragana_mixed(key, value):
    i = 0
    # append garbage to key so it has the same length
    key = key + "_"*(len(value)-len(key))
    corrected = ""

    for k, v in zip(key, value):
        # cases when key actually includes katakana
        if k == v:
            corrected += v
        # else this is most likely hiragana to convert
        elif is_katakana(v):
            corrected += to_hiragana(v)
        # else probably a symbol we don't want to do anything
        else:
            corrected += v

    return corrected

def correct_hiragana(value):
    return "".join(map(to_hiragana, value))

def correct_word(key, value):
    if is_katakana(key[0]):
        return correct_hiragana_mixed(key, value)
    elif is_katakana(key[-1]):
        return correct_hiragana_mixed(key[::-1], value[::-1])[::-1]
    else:
        return correct_hiragana(value)

def format_accent(entry):
    # zero pad the accent
    accents = entry.ac
    accents = "0"*(len(chars)-len(accents))+accents
    # correct the kana
    chars = correct_word(entry.nhk, entry.midashigo1)

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

