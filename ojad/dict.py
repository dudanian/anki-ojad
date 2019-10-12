import os

DIR_PATH = os.path.dirname(os.path.normpath(__file__))
DICT_NAMES = [
    "group1",
    "group2",
    "group3",
    "ikei",
    "nakei",
    "meishi",
]
DICT_FILES = map(lambda x: os.path.join(DIR_PATH, f"{x}.txt"), DICT_NAMES)

ojad_dict = {}

def generate_dict():
    for dict_file in DICT_FILES:
        with open(dict_file, "r") as f:
            # ignore first line comment
            f.readline()
            for line in f:
                key, value = line.strip().split(",")
                if key in ojad_dict:
                    if value not in ojad_dict[key]:
                        ojad_dict[key].append(value)
                else:
                    ojad_dict[key] = [value]

def get_pronunciations(text):
    if not ojad_dict:
        generate_dict()

    return ojad_dict.get(text, [])
