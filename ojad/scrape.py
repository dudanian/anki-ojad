from datetime import datetime

from fetch import fetch
from parse import jishokei_entries


# category codes from OJAD
CATEGORIES = {
    "group1": 1,
    "group2": 2,
    "group3": 3,
    "ikei": 4,
    "nakei": 5,
    "meishi": 6,
}


def scrape(category):
    cno = CATEGORIES[category]
    remove_last_na = category == "nakei"

    with open(f"{category}.txt", "w") as f:
        f.write(f"Generated at: {datetime.now()}")

        page = 1
        count = 0
        last = -1
        while count != last:
            last = count
            p = fetch(limit=100, page=page, category=cno)
            for midashi, annotated in jishokei_entries(p, remove_last_na):
                f.write(f"\n{midashi},{annotated}")
                count += 1

            page += 1

    print(f"{category}: Wrote {count} entries!")


def validate():
    d = {}
    for n in CATEGORIES.keys():
        with open(f"{n}.txt", "r") as f:
            # ignore first line comment
            f.readline()
            for line in f:
                key, value = line.strip().split(",")
                if key in d:
                    d[key].append(value)
                else:
                    d[key] = [value]


def scrape_test():
    p = fetch(word="便利")
    for midashi, annotated in jishokei_entries(p, na=True):
        print(midashi, annotated)

if __name__ == "__main__":
    #scrape("group1")
    #scrape("group2")
    #scrape("group3")
    #scrape("ikei")
    #scrape("nakei")
    #scrape("meishi")
    validate()
    #scrape_test()
