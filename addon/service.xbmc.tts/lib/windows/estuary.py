# -*- coding: utf-8 -*-
"""Focused speech support for Estuary's multi-region home window."""
import xbmc

from .base import DefaultWindowReader
from lib import util


class EstuaryHomeReader(DefaultWindowReader):
    """Give Estuary home widgets stable labels and useful region context."""

    ID = 'estuaryhome'
    HOME_MENU_ID = 9000
    HIDDEN_FOCUS_IDS = (20000, 20001)

    # control id: (home-section Kodi string id, widget-heading Kodi string id)
    WIDGETS = {
        4100: (1, 20094),
        5100: (342, 31010), 5200: (342, 20386), 5300: (342, 31007),
        5400: (342, 31006), 5500: (342, 135), 5600: (342, 31075),
        5900: (342, 31148),
        6100: (20343, 626), 6200: (20343, 20387),
        6300: (20343, 31122), 6400: (20343, 135),
        6500: (20343, 20388), 6900: (20343, 31148),
        7100: (2, 517), 7200: (2, 359), 7300: (2, 31012),
        7400: (2, 31013), 7500: (2, 31014), 7600: (2, 31011),
        7900: (2, 31148),
        8100: (24001, 1037), 8200: (24001, 1038),
        8300: (24001, 1043), 8400: (24001, 20244),
        8500: (24001, 1039), 8700: (24001, 35049),
        8900: (24001, 31148),
        11100: (3, 20094), 11200: (3, 136), 11900: (3, 31148),
        12200: (19020, 31016), 12300: (19020, 31015),
        12400: (19020, 19040), 12500: (19020, 19173),
        12600: (19020, 19337), 12900: (19020, 31148),
        13200: (19021, 31018), 13300: (19021, 31015),
        13400: (19021, 19040), 13500: (19021, 19174),
        13600: (19021, 19337), 13900: (19021, 31148),
        14100: (10134, 10134),
        15100: (8, 33036), 15200: (8, 31019),
        16200: (20389, 31013), 16300: (20389, 20390),
        16400: (20389, 31151), 16500: (20389, 31152),
        16600: (20389, 20388), 16900: (20389, 31148),
        17200: (15016, 35049),
    }

    UTILITY_BUTTONS = {
        801: 137,       # Search
        802: 21417,     # Settings
        803: 31000,     # Full screen
        804: 33060,     # Power
        805: 31000,     # Full screen / player controls
    }

    def _localized(self, string_id):
        return xbmc.getLocalizedString(string_id) or u''

    def getHeading(self):
        # The service already announces the Home window name.  Estuary's
        # Control 1 is not a reliable heading and can contain stale text.
        return u''

    def getWindowTexts(self):
        # Do not parse decorative home labels, clock, weather, and widget
        # headers as one large announcement when entering the home window.
        return None

    def getControlDescription(self, controlID):
        if controlID in self.HIDDEN_FOCUS_IDS:
            return u''
        if controlID == self.HOME_MENU_ID:
            return u'{0}: {1}'.format(util.T(32175), self._localized(10000))
        if controlID in self.UTILITY_BUTTONS:
            return util.T(32235)
        widget = self.WIDGETS.get(controlID)
        if not widget:
            return DefaultWindowReader.getControlDescription(self, controlID)
        section = self._localized(widget[0])
        area = self._localized(widget[1])
        parts = []
        if section:
            parts.append(u'{0}: {1}'.format(util.T(32175), section))
        if area and area != section:
            parts.append(u'{0}: {1}'.format(util.T(32176), area))
        return u', '.join(parts)

    def _containerLabel(self, controlID, name):
        return xbmc.getInfoLabel(
            'Container({0}).ListItem.{1}'.format(controlID, name))

    def _focusedItemIdentity(self, controlID, text):
        container = 'Container({0})'.format(controlID)
        current = xbmc.getInfoLabel(container + '.CurrentItem')
        dbid = self._containerLabel(controlID, 'DBID') or xbmc.getInfoLabel('ListItem.DBID')
        dbtype = self._containerLabel(controlID, 'DBTYPE') or xbmc.getInfoLabel('ListItem.DBTYPE')
        path = (self._containerLabel(controlID, 'FileNameAndPath') or
                xbmc.getInfoLabel('ListItem.FileNameAndPath'))
        return u'\x1f'.join((u'{0}'.format(self.winID), u'{0}'.format(controlID),
                              current or u'', dbtype or u'', dbid or u'',
                              path or u'', text or u''))

    def getControlText(self, controlID):
        if self.slideoutHasFocus():
            return self.getSlideoutText(controlID)
        if not controlID or controlID in self.HIDDEN_FOCUS_IDS:
            return (u'', u'')

        # Estuary has many simultaneous home containers.  Global ListItem
        # labels can briefly refer to the previous widget, so always query the
        # focused container first.
        text = self._containerLabel(controlID, 'Label')
        if not text:
            text = self._containerLabel(controlID, 'Title')
        if not text:
            text = xbmc.getInfoLabel('Control.GetLabel({0})'.format(controlID))
        if not text:
            text = xbmc.getInfoLabel('System.CurrentControl')
        if not text:
            text = xbmc.getInfoLabel('ListItem.Label') or xbmc.getInfoLabel('ListItem.Title')
        if not text:
            return (u'', u'')
        compare = self._focusedItemIdentity(controlID, text)
        return (self._decorateControlText(controlID, text), compare)
