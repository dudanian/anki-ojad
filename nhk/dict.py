import csv
import os

from collections import namedtuple

PITCH_RAISE = "["
PITCH_LOWER = "]"
PITCH_STEADY = "-"

#DIR_PATH = os.path.dirname(os.path.normpath(__file__))
DIR_PATH = "/home/aduda/.local/share/Anki2/addons21/something/else"
NHK_PATH = os.path.normpath(os.path.join(DIR_PATH, "..", "..", "932119536"))
RAW_NHK_DICT = os.path.join(NHK_PATH, "ACCDB_unicode.csv")
NHK_DICT = os.path.join(DIR_PATH, "dict.txt")

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
    'ac', # accent length, if shorter than numchars, have to 0 pad front
])

def format_accent(entry):
    chars = entry.midashigo1
    # zero pad the accent
    accents = entry.ac
    accents = "0"*(len(chars)-len(accents))+accents

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
    for entry in map(AccentEntry._make, csv.reader(open(RAW_NHK_DICT, "r"))):
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


if __name__ == "__main__":
    build_dict()
