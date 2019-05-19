from .lookup import fetch_formatted_entries

from anki.hooks import addHook
from aqt import mw
from aqt.utils import showInfo

config = mw.addonManager.getConfig(__name__)


def validNoteType(note_model):
    note_name = note_model['name'].lower()
    for note_type in config['noteTypes']:
        if note_type.lower() in note_name:
            return True

    return False


def onFocusLost(flag, note, fidx):
    if not validNoteType(note.model()):
        return flag

    # make these configurable later
    src_field = "Expression"
    dst_field = "Pronunciation"

    fields = mw.col.models.fieldNames(note.model())
    triggered_field = fields[fidx]

    if triggered_field != src_field:
        return flag

    if dst_field not in note:
        return flag

    if note[dst_field]:
        return flag

    src_text = mw.col.media.strip(note[src_field])
    if not src_text:
        return flag

    # this might crash, which isn't great but makes debugging easier
    entries = fetch_formatted_entries(src_text)
    note[dst_field] = "<br />".join(entries["jisho"])

    # return true if made any change
    return True


addHook("editFocusLost", onFocusLost)

