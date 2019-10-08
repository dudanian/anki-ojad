import os

DIR_PATH = os.path.dirname(os.path.normpath(__file__))
DICT_PATH = os.path.join(DIR_PATH, "scraping")
DICT_NAMES = [
    "group1",
    "group2",
    "group3",
    "ikei",
    "nakei",
    "meishi",
]
DICT_FILES = map(lambda x: os.path.join(DICT_PATH, f"{x}.txt"), DICT_NAMES)

scraped_dict = {}

def generate_dict():
    for dict_file in DICT_FILES:
        with open(dict_file, "r") as f:
            # ignore first line comment
            f.readline()
            for line in f:
                key, value = line.strip().split(",")
                if key in scraped_dict:
                    scraped_dict[key].append(value)
                else:
                    scraped_dict[key] = [value]

def get_pronunciations(text):
    if not scraped_dict:
        generate_dict()

    return scraped_dict.get(text, [])
