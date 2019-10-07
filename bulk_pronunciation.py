from aqt.qt import *
from anki.hooks import addHook
from .pronunciation import validNoteType, regeneratePronunciation
from aqt import mw

def regeneratePronunciations(nids):
    mw.checkpoint("Bulk-add Pronunciations")
    mw.progress.start()
    for nid in nids:
        note = mw.col.getNote(nid)
        if not validNoteType(note.model()):
            continue
        fields = mw.col.models.fieldNames(note.model())
        for src in fields:
            regeneratePronunciation(note, src)
        note.flush()
    mw.progress.finish()
    mw.reset()


def setupMenu(browser):
    a = QAction("Bulk-add Pronunciations", browser)
    a.triggered.connect(lambda: onRegenerate(browser))
    browser.form.menuEdit.addSeparator()
    browser.form.menuEdit.addAction(a)


def onRegenerate(browser):
    regeneratePronunciations(browser.selectedNotes())


addHook("browser.setupMenus", setupMenu)
