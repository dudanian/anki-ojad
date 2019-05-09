from urllib.parse import quote
from urllib.request import urlopen

from .ojad import parse_html, format_entries

def fetch_entries(text):
    baseUrl = "http://www.gavo.t.u-tokyo.ac.jp/ojad/search/index/display:print" + \
        "/sortprefix:accent/narabi1:kata_asc/narabi2:accent_asc/narabi3:mola_asc/yure:" + \
        "visible" + "/curve:invisible/details:invisible/limit:1/word:"
    url = baseUrl + quote(text.encode("utf-8"))
    raw_html = urlopen(url).read()
    return parse_html(raw_html.decode("utf-8"))

def fetch_formatted_entries(text):

    return format_entries(fetch_entries(text))

if __name__ == "__main__":
    print(fetch_entries("会社員"))
    print(fetch_formatted_entries("会社員"))
    