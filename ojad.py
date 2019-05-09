from html.parser import HTMLParser


def get_classnames(attrs):
    for attr in attrs:
        if attr[0] == "class":
            return attr[1].split()
    return []


class HTMLHandler():

    def __init__(self, parent):
        self.tag_stack = []
        self.parent = parent

    def starttag(self, tag, attrs):
        pass

    def endtag(self, tag):
        expected_tag = self.tag_stack.pop()
        if tag != expected_tag:
            raise Exception("End tag does not match expected end tag. Expected:", expected_tag, "Found:", tag)

        if len(self.tag_stack) == 0:
            return self.parent

        return self

    def handle_data(self, data):
        pass

    def final_data(self):
        pass


class BaseHandler(HTMLHandler):

    def __init__(self, entries):
        HTMLHandler.__init__(self, None)
        self.entries = entries

    def starttag(self, tag, attrs):
        classnames = get_classnames(attrs)
        if "katsuyo_jisho_js" in classnames:
            self.entries["jisho"] = []
            handler = KatsuyoHandler(self, self.entries["jisho"])
            return handler.starttag(tag, attrs)

        return self

    def endtag(self, tag):
        return self
        

class KatsuyoHandler(HTMLHandler):

    def __init__(self, parent, words):
        HTMLHandler.__init__(self, parent)
        self.words = words

    def starttag(self, tag, attrs):
        classnames = get_classnames(attrs)

        if "accented_word" in classnames:
            self.words.append([])
            handler = AccentedWordHandler(self, self.words[-1])
            return handler.starttag(tag, attrs)

        self.tag_stack.append(tag)
        return self


class AccentedWordHandler(HTMLHandler):

    def __init__(self, parent, moras):
        HTMLHandler.__init__(self, parent)
        self.moras = moras
        self.next_data = False

    def starttag(self, tag, attrs):
        classnames = get_classnames(attrs)

        for classname in classnames:
            if "mola_-" in classname:
                # check for the accent
                if "accent_plain" in classnames:
                    self.next_accent = "plain"
                elif "accent_top" in classnames:
                    self.next_accent = "top"
                else:
                    self.next_accent = "low"

        # check for the char data
        if "char" in classnames:
            self.next_data = True

        self.tag_stack.append(tag)
        return self

    def handle_data(self, data):
        if self.next_data:
            data = data.strip()
            if not data:
                raise Exception("Mora data is empty?")

            self.moras.append((data.strip(), self.next_accent))
            # need to reset because defaults to low
            self.next_data = False


def parse_html(string):

    class OJADParser(HTMLParser):

        def __init__(self, entries):
            HTMLParser.__init__(self)
            self.handler = BaseHandler(entries)

        def handle_starttag(self, tag, attrs):
            self.handler = self.handler.starttag(tag, attrs)

        def handle_endtag(self, tag):
            self.handler = self.handler.endtag(tag)

        def handle_data(self, data):
            self.handler.handle_data(data)

    entries = {}
    OJADParser(entries).feed(string)
    return entries


def compress_moras(word):
    """
    I needed to do this to fix a bug with small characters.
    Basically there would be two top accents because OJAD separates them.
    """
    new_word = []
    current_mora, current_accent = word[0]
    for next_mora, next_accent in word[1:]:
        if current_accent == next_accent:
            current_mora += next_mora
        else:
            new_word.append((current_mora, current_accent))
            current_mora = next_mora
            current_accent = next_accent
    else:
        new_word.append((current_mora, current_accent))
    
    return new_word


def format_entries(entries):
    new_entries = {}

    for conj, words in entries.items():
        new_words = []

        for word in words:
            word = compress_moras(word)
            new_word = ""
            high = ""

            for mora, accent in word:
                if accent == "low":
                    new_word += mora
                elif accent == "plain":
                    high += mora
                elif accent == "top":
                    high += mora
                    new_word = "".join([new_word, '<span class="accent_high accent_edge">', high, '</span>'])
                    high = ""

            if high:
                new_word = "".join([new_word, '<span class="accent_high">', high, '</span>'])

            new_words.append(new_word)
        new_entries[conj] = new_words

    return new_entries


# ghetto test
if __name__ == '__main__':
    # some sample text taken from ojad
    test = '''<tbody>
    <tr id="word_9346">
        <td class="visible"><a href="#" onclick="$(this).parents('#word_table > tbody > tr').hide();return false;">×</a></td>
        <td class="midashi">
            <div class="midashi_wrapper">
                <p class="midashi_word">何</p>
            </div>
        </td>
        <td class="katsuyo katsuyo_jisho_js">
            <div class="katsuyo_proc">
                <p>
                    <span class="katsuyo_accent">
                        <span class="accented_word">
                            <span class=" accent_top mola_-2">
                                <span class="inner">
                                    <span class="char">な</span>
                                </span>
                            </span>
                            <span class="mola_-1">
                                <span class="inner">
                                    <span class="char">に</span>
                                </span>
                            </span>
                        </span>
                    </span>
                </p>
                <div class="katsuyo_proc_button clearfix"></div>
            </div>
        </td>
        <td class="katsuyo katsuyo_masu_js"></td>
        <td class="katsuyo katsuyo_te_js"></td>
        <td class="katsuyo katsuyo_ta_js"></td>
        <td class="katsuyo katsuyo_nai_js"></td>
        <td class="katsuyo katsuyo_nakatta_js"></td>
        <td class="katsuyo katsuyo_ba_js"></td>
        <td class="katsuyo katsuyo_shieki_js"></td>
        <td class="katsuyo katsuyo_ukemi_js"></td>
        <td class="katsuyo katsuyo_meirei_js"></td>
        <td class="katsuyo katsuyo_kano_js"></td>
        <td class="katsuyo katsuyo_ishi_js"></td>
    </tr>
</tbody>'''
    print(parse(test))
