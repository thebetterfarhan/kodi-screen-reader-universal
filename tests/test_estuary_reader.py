"""Mocked regression tests for Estuary home speech."""
import importlib.util
import os
import sys
import types
import unittest


def load_reader(labels, localized=None, visible=None):
    localized = localized or {}
    visible = visible or set()
    xbmc = types.ModuleType('xbmc')
    xbmc.getInfoLabel = lambda label: labels.get(label, '')
    xbmc.getLocalizedString = lambda value: localized.get(value, '')
    xbmc.getCondVisibility = lambda value: value in visible
    xbmcgui = types.ModuleType('xbmcgui')
    xbmcgui.Window = lambda value: None
    util = types.ModuleType('lib.util')
    words = {32175: 'section', 32176: 'area', 32232: 'list item',
             32233: '{0} of {1}', 32235: 'button', 32200: 'selected'}
    util.T = lambda value: words.get(value, str(value))
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
    skintables.CURRENT_SKIN = 'estuary'
    skintables.getControlText = lambda win, control: None
    sys.modules.update({'xbmc': xbmc, 'xbmcgui': xbmcgui, 'lib': lib,
                        'lib.util': util, 'windows': windows,
                        'windows.guitables': guitables,
                        'windows.windowparser': windowparser,
                        'windows.skintables': skintables})
    root = os.path.join(os.path.dirname(__file__), '..', 'addon', 'service.xbmc.tts',
                        'lib', 'windows')
    base_spec = importlib.util.spec_from_file_location('windows.base', os.path.join(root, 'base.py'))
    base = importlib.util.module_from_spec(base_spec)
    sys.modules['windows.base'] = base
    base_spec.loader.exec_module(base)
    spec = importlib.util.spec_from_file_location('windows.estuary', os.path.join(root, 'estuary.py'))
    module = importlib.util.module_from_spec(spec)
    sys.modules['windows.estuary'] = module
    spec.loader.exec_module(module)
    reader = module.EstuaryHomeReader.__new__(module.EstuaryHomeReader)
    reader.winID = 10000
    reader.service = types.SimpleNamespace(speakControlRoles=True,
                                           speakItemPosition=True,
                                           speakSelectedState=True)
    reader.slideoutHasFocus = lambda: False
    return reader


class EstuaryHomeReaderTests(unittest.TestCase):
    def test_prefers_focused_container_over_stale_global_title(self):
        labels = {'ListItem.Title': 'Wrong old widget',
                  'Container(5100).ListItem.Label': 'Correct movie',
                  'Container(5100).CurrentItem': '2',
                  'Container(5100).NumItems': '8'}
        spoken, identity = load_reader(labels).getControlText(5100)
        self.assertEqual(spoken, 'Correct movie, list item, 2 of 8')
        self.assertIn('Correct movie', identity)
        self.assertNotIn('Wrong old widget', spoken)

    def test_announces_section_and_widget_area(self):
        localized = {342: 'Movies', 31010: 'In progress'}
        description = load_reader({}, localized).getControlDescription(5100)
        self.assertEqual(description, 'section: Movies, area: In progress')

    def test_home_menu_and_utility_button_have_context(self):
        reader = load_reader({}, {10000: 'Home'})
        self.assertEqual(reader.getControlDescription(9000), 'section: Home')
        self.assertEqual(reader.getControlDescription(802), 'button')

    def test_hidden_focus_transfer_controls_are_silent(self):
        labels = {'System.CurrentControl': 'stale'}
        reader = load_reader(labels)
        self.assertEqual(reader.getControlText(20000), ('', ''))
        self.assertEqual(reader.getControlDescription(20000), '')


if __name__ == '__main__':
    unittest.main()
