"""Mocked focus-identity regression tests; run with Python 3.8+."""
import importlib.util
import os
import sys
import types
import unittest


def load_reader(labels):
    xbmc = types.ModuleType('xbmc')
    xbmc.getInfoLabel = lambda label: labels.get(label, '')
    xbmc.getCondVisibility = lambda value: False
    xbmcgui = types.ModuleType('xbmcgui')
    xbmcgui.Window = lambda value: None
    util = types.ModuleType('lib.util')
    util.T = lambda value: str(value)
    lib = types.ModuleType('lib')
    lib.util = util
    windows = types.ModuleType('windows')
    windows.__path__ = []
    guitables = types.ModuleType('windows.guitables')
    guitables.getWindowName = lambda value: ''
    guitables.getWindowTexts = lambda value: None
    guitables.getExtraTexts = lambda value: None
    guitables.getListItemProperty = lambda value: None
    guitables.getItemExtraTexts = lambda value: None
    guitables.getSongInfo = lambda: None
    windowparser = types.ModuleType('windows.windowparser')
    skintables = types.ModuleType('windows.skintables')
    skintables.CURRENT_SKIN = None
    skintables.getControlText = lambda win, control: None
    sys.modules.update({'xbmc': xbmc, 'xbmcgui': xbmcgui, 'lib': lib,
                        'lib.util': util, 'windows': windows,
                        'windows.guitables': guitables,
                        'windows.windowparser': windowparser,
                        'windows.skintables': skintables})
    path = os.path.join(os.path.dirname(__file__), '..', 'addon', 'service.xbmc.tts', 'lib', 'windows', 'base.py')
    spec = importlib.util.spec_from_file_location('windows.base_under_test', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    reader = module.DefaultWindowReader.__new__(module.DefaultWindowReader)
    reader.winID = 100
    reader.service = types.SimpleNamespace(speakControlRoles=True,
                                           speakItemPosition=True,
                                           speakSelectedState=True)
    reader.slideoutHasFocus = lambda: False
    return reader


class FocusIdentityTests(unittest.TestCase):
    def test_adjacent_duplicate_labels_have_different_container_identity(self):
        labels = {'ListItem.Title': 'Duplicate', 'Container(50).CurrentItem': '1'}
        reader = load_reader(labels)
        first = reader.getControlText(50)[1]
        labels['Container(50).CurrentItem'] = '2'
        second = reader.getControlText(50)[1]
        self.assertNotEqual(first, second)

    def test_in_place_label_changes_are_not_suppressed(self):
        labels = {'ListItem.Title': 'Old label', 'Container(50).CurrentItem': '2'}
        reader = load_reader(labels)
        first = reader.getControlText(50)[1]
        labels['ListItem.Title'] = 'Updated label'
        self.assertNotEqual(first, reader.getControlText(50)[1])

    def test_stable_database_identity_distinguishes_same_label(self):
        labels = {'ListItem.Title': 'Same', 'ListItem.DBID': '101', 'ListItem.DBTYPE': 'movie'}
        reader = load_reader(labels)
        first = reader.getControlText(50)[1]
        labels['ListItem.DBID'] = '102'
        self.assertNotEqual(first, reader.getControlText(50)[1])


if __name__ == '__main__':
    unittest.main()
