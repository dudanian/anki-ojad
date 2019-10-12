import re
import xml.etree.ElementTree as et


PITCH_RAISE = "["
PITCH_LOWER = "]"
PITCH_STEADY = "-"


class OJADPage:
    def __init__(self, text):
        self.root = et.fromstring(text)

    def not_found(self):
        elem = self.root.find(".//div[@id='search_result_message']")

        # elem is Falsy, this is just stupid
        if elem is not None and elem.text:
            if elem.text.strip() == "見つかりませんでした。":
                return True
        return False

    def entries(self):
        elems = self.root.findall(".//tr[@id]")
        # elementtree doesn't support regex, so filter myself
        return [OJADEntry(x) for x in elems if re.match("word_\d+", x.get("id"))]


class OJADEntry:
    def __init__(self, root):
        self.root = root

    def midashi(self):
        elem = self.root.find(".//p[@class='midashi_word']")
        # might contain desu form, I don't want that
        def without_desu(text):
            return text.split("・")[0]
        # also na kei adds a na for whatever reason
        def without_na(text):
            return text.replace("[な]", "")

        return without_na(without_desu(elem.text.strip()))

    def jishokei(self, remove_last_na=False):
        elem = self.root.find(".//td[@class='katsuyo katsuyo_jisho_js']")
        return OJADConjugation(elem).annotated(remove_last_na)


class OJADConjugation:
    def __init__(self, root):
        self.root = root

    def _accented_chars(self):
        def with_accent(elem):
            accent = "low"
            match = re.search("accent_(plain|top)", elem.get("class"))
            if match:
                accent = match.group(1)

            chars = elem.findall(".//span[@class='char']")
            char = "".join(map(lambda x: x.text.strip(), chars))
            return (char, accent)

        elems = self.root.findall(".//span[@class]")
        return [with_accent(x) for x in elems if re.search("mola_-\d+", x.get("class"))]

    def annotated(self, remove_last_na=False):
        last = "low"
        word = ""

        chars = self._accented_chars()
        if remove_last_na and chars and chars[-1][0] == "な":
            chars = chars[:-1]

        for char, accent in chars:
            if accent != "low" and last == "low":
                word += PITCH_RAISE
            word += char
            if accent == "top":
                word += PITCH_LOWER
            last = accent

        if last == "plain":
            word += PITCH_STEADY
        return word


def jishokei_entries(text, remove_last_na=False):
    for entry in OJADPage(text).entries():
        yield (entry.midashi(), entry.jishokei(remove_last_na))


if __name__ == "__main__":
    with open("web.html", "r") as f:
        error = f.read()
        for a,b in jishokei_entries(error):
            print(a, b)
