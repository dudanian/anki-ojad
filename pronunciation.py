import re

from anki.hooks import addHook
from aqt import mw

from .ojad.dict import get_pronunciations as get_ojad_pronunciations
from .nhk.dict import get_pronunciations as get_nhk_pronunciations

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

    fields = mw.col.models.fieldNames(note.model())
    src = fields[fidx]
    if not regeneratePronunciation(note, src):
        return flag
    return True

def regeneratePronunciation(note, src):
    # make these configurable later
    src_field = "Expression"
    dst_field = "Pronunciation"

    if src != src_field:
        return False

    if dst_field not in note:
        return False

    if note[dst_field]:
        return False

    src_text = mw.col.media.strip(note[src_field])
    if not src_text:
        return False

    # remove possible parens
    src_text = re.sub("（.+?）", "", src_text)
    # split by japanese slash
    words = src_text.split("／")
    #entries = get_ojad_pronunciations(src_text)
    entries = []
    for word in words:
        entries.extend(get_nhk_pronunciations(word))

    note[dst_field] = "<br>".join(entries)

    # return true if made any change
    return True

addHook("editFocusLost", onFocusLost)
