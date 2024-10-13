from aqt import mw
from aqt.browser import Browser
from aqt.qt import *
from anki.hooks import addHook
from aqt.utils import (
    ensure_editor_saved,
    skip_if_selection_is_empty,
    showInfo,
    qconnect
)
from .dict_open_api import dictionary

CONFIG = mw.addonManager.getConfig(__name__)


@skip_if_selection_is_empty
@ensure_editor_saved
def add_hanja_and_pos(browser: Browser) -> None:
    
    nids = browser.table.get_selected_note_ids()
    total_notes = len(nids)

    progress_dialog = QProgressDialog('Processing...', 'Cancel', 0, total_notes, mw)
    progress_dialog.setWindowTitle(f'Adding to {total_notes} notes')
    progress_dialog.setModal(True)
    progress_dialog.setMinimumDuration(0)

    for index, nid in enumerate(nids):
        if progress_dialog.wasCanceled():
            break

        input_field = CONFIG['input_field']
        hanja_field = CONFIG['hanja_field']
        pos_field = CONFIG['pos_field']
        note = mw.col.get_note(nid)
        hanja, pos = dictionary(note[input_field])
        if hanja:
            note[hanja_field] = hanja
        if pos:
            note[pos_field] = pos
        mw.col.update_note(note)

        progress_dialog.setValue(index + 1)

    progress_dialog.close()
    showInfo('Done!')
    mw.reset()


@skip_if_selection_is_empty
@ensure_editor_saved
def add_hanja(browser: Browser) -> None:
    
    nids = browser.table.get_selected_note_ids()
    total_notes = len(nids)

    progress_dialog = QProgressDialog('Processing...', 'Cancel', 0, total_notes, mw)
    progress_dialog.setWindowTitle(f'Adding Hanja to {total_notes} notes')
    progress_dialog.setModal(True)
    progress_dialog.setMinimumDuration(0)

    for index, nid in enumerate(nids):
        if progress_dialog.wasCanceled():
            break

        input_field = CONFIG['input_field']
        hanja_field = CONFIG['hanja_field']
        note = mw.col.get_note(nid)
        hanja, _ = dictionary(note[input_field])
        if hanja:
            note[hanja_field] = hanja
            mw.col.update_note(note)

        progress_dialog.setValue(index + 1)

    progress_dialog.close()
    showInfo('Done!')
    mw.reset()


@skip_if_selection_is_empty
@ensure_editor_saved
def add_pos(browser: Browser) -> None:
    
    nids = browser.table.get_selected_note_ids()
    total_notes = len(nids)

    progress_dialog = QProgressDialog('Processing...', 'Cancel', 0, total_notes, mw)
    progress_dialog.setWindowTitle(f'Adding to {total_notes} notes')
    progress_dialog.setModal(True)
    progress_dialog.setMinimumDuration(0)

    for index, nid in enumerate(nids):
        if progress_dialog.wasCanceled():
            break

        input_field = CONFIG['input_field']
        pos_field = CONFIG['pos_field']
        note = mw.col.get_note(nid)
        _, pos = dictionary(note[input_field])
        if pos:
            note[pos_field] = pos
            mw.col.update_note(note)

        progress_dialog.setValue(index + 1)

    progress_dialog.close()
    showInfo('Done!')
    mw.reset()


def setup_menu(browser: Browser) -> None:
    menu_notes = browser.form.menu_Notes
    menu_notes.addSeparator()
    hanja_pos = QMenu('Korean Dictionary', parent=menu_notes)
    hanja_pos.setObjectName('hanja_pos')

    act = QAction('Add Hanja', hanja_pos)
    act.setObjectName('add_hanja')
    qconnect(act.triggered, lambda: add_hanja(browser))
    hanja_pos.addAction(act)

    act = QAction('Add POS', hanja_pos)
    act.setObjectName('add_pos')
    qconnect(act.triggered, lambda: add_pos(browser))
    hanja_pos.addAction(act)

    act = QAction('Add Hanja and POS', hanja_pos)
    act.setObjectName('add_hanja_and_pos')
    qconnect(act.triggered, lambda: add_hanja_and_pos(browser))
    hanja_pos.addAction(act)

    menu_notes.addMenu(hanja_pos)


def main():
    addHook('browser.setupMenus', setup_menu)


main()
