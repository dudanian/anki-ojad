from urllib.parse import quote
from urllib.request import urlopen


def fetch(yure=False, limit=None, page=None, category=None, word=None):
    def make_url():
        # things I don't expect to change
        url = "http://www.gavo.t.u-tokyo.ac.jp/ojad/search/index/display:print" + \
            "/sortprefix:accent/narabi1:kata_asc/narabi2:accent_asc/narabi3:mola_asc" + \
            "/curve:invisible/details:invisible"

        options = {}
        options["yure"] = "visible" if yure else "invisible"
        if limit:
            options["limit"] = limit
        if page:
            options["page"] = page
        if category:
            options["category"] = category
        if word:
            options["word"] = quote(word.encode("utf-8"))

        for key, value in options.items():
            url += f"/{key}:{value}"
        
        return url

    raw_html = urlopen(make_url()).read()
    return raw_html.decode("utf-8")


if __name__ == "__main__":
    web = fetch(limit=1, word="会社員")
    with open("web.html", "w") as f:
        f.write(web)
