# -*- coding: utf-8 -*-
import xbmc, xbmcgui
from . import guitables
from . import windowparser
from . import skintables
from lib import util

CURRENT_SKIN = skintables.CURRENT_SKIN

def parseItemExtra(controlID,current=None):
    texts = windowparser.getWindowParser().getListItemTexts(controlID)
    if current and texts:
        while current in texts: texts.pop(texts.index(current))
    return texts

class WindowHandlerBase:
    ID = None
    def __init__(self,win_id=None,service=None):
        self.service = service
        self._reset(win_id)

    def _reset(self,win_id):
        self.winID = win_id
        self.init()

    def window(self):
        return xbmcgui.Window(self.winID)

    def visible(self):
        return xbmc.getCondVisibility('Window.IsVisible({0})'.format(self.winID))

    def init(self): pass

    def getMonitoredText(self,isSpeaking=False): return None

    def close(self): pass

class WindowReaderBase(WindowHandlerBase):
    _slideoutGroupID = 9000

    def getName(self): return guitables.getWindowName(self.winID)

    def getHeading(self): return None

    def getWindowTexts(self): return None

    def getControlDescription(self,controlID): return None

    def getControlText(self,controlID):
        text = xbmc.getInfoLabel('System.CurrentControl')
        return (text,text)

    def getControlPostfix(self, controlID, ):
        if not self.service.speakListCount:
            return u''
        numItems = xbmc.getInfoLabel('Container({0}).NumItems'.format(self.service.controlID))
        if numItems:
            return u'... {0} {1}'.format(numItems,numItems != '1' and util.T(32107) or util.T(32106))
        return u''

    def getSecondaryText(self): return None

    def getItemExtraTexts(self,controlID): return None

    def getWindowExtraTexts(self):
        texts = guitables.getExtraTexts(self.winID)
        if not texts: texts = windowparser.getWindowParser().getWindowTexts()
        return texts or None

    def slideoutHasFocus(self):
        return xbmc.getCondVisibility('ControlGroup({0}).HasFocus(0)'.format(self._slideoutGroupID))

    def getSettingControlText(self,controlID):
        text = xbmc.getInfoLabel('System.CurrentControl')
        if text.endswith(')'): #Skip this most of the time
            text = text.replace('( )','{0} {1}'.format(self.service.tts.pauseInsert,util.T(32174))).replace('(*)','{0} {1}'.format(self.service.tts.pauseInsert,util.T(32173))) #For boolean settings
        return text

    def getSlideoutText(self,controlID):
        text = self.getSettingControlText(controlID)
        if not text: return (u'',u'')
        return (text,text)

class DefaultWindowReader(WindowReaderBase):
    ID = 'default'

    def _focusedItemIdentity(self, controlID, text):
        """Return a focus identity independent of the spoken label.

        CurrentItem is Kodi's focused container position, not a visible row.
        It therefore changes while a list scrolls even if the same row remains
        on screen.  A DB id/path is included when Kodi exposes one.
        """
        container = 'Container({0})'.format(controlID)
        current_item = xbmc.getInfoLabel(container + '.CurrentItem')
        if not current_item:
            current_item = xbmc.getInfoLabel('ListItem.CurrentItem')
        dbid = xbmc.getInfoLabel('ListItem.DBID')
        dbtype = xbmc.getInfoLabel('ListItem.DBTYPE')
        path = xbmc.getInfoLabel('ListItem.FileNameAndPath')
        # Include text so that an in-place label update is still announced.
        return u'\x1f'.join((u'{0}'.format(self.winID), u'{0}'.format(controlID),
                              current_item or u'', dbtype or u'', dbid or u'',
                              path or u'', text or u''))

    def _decorateControlText(self, controlID, text):
        service = self.service
        current = xbmc.getInfoLabel('Container({0}).CurrentItem'.format(controlID)) or xbmc.getInfoLabel('ListItem.CurrentItem')
        total = xbmc.getInfoLabel('Container({0}).NumItems'.format(controlID))
        parts = [text]
        if current and getattr(service, 'speakControlRoles', True):
            parts.append(util.T(32232))
        if current and total and getattr(service, 'speakItemPosition', True):
            parts.append(util.T(32233).format(current, total))
        if getattr(service, 'speakSelectedState', True) and xbmc.getCondVisibility('Container({0}).ListItem.IsSelected'.format(controlID)):
            parts.append(util.T(32200))
        return u', '.join([part for part in parts if part])

    def getHeading(self):
        return xbmc.getInfoLabel('Control.GetLabel(1)') or u''

    def getWindowTexts(self):
        return guitables.getWindowTexts(self.winID)

    def getControlDescription(self,controlID):
        return skintables.getControlText(self.winID, controlID) or u''

    def getControlText(self,controlID):
        if self.slideoutHasFocus():
            return self.getSlideoutText(controlID)

        if not controlID: return (u'',u'')
        text = xbmc.getInfoLabel('ListItem.Title')
        if not text: text = xbmc.getInfoLabel('Container({0}).ListItem.Label'.format(controlID))
        if not text: text = xbmc.getInfoLabel('Control.GetLabel({0})'.format(controlID))
        if not text: text = xbmc.getInfoLabel('System.CurrentControl')
        if not text: return (u'',u'')
        compare = self._focusedItemIdentity(controlID, text)
        return (self._decorateControlText(controlID, text),compare)

    def getSecondaryText(self):
        return guitables.getListItemProperty(self.winID)

    def getItemExtraTexts(self,controlID):
        text = guitables.getItemExtraTexts(self.winID)
        if not text: text = xbmc.getInfoLabel('ListItem.Plot')
        if not text: text = xbmc.getInfoLabel('Container.ShowPlot')
        if not text: text = xbmc.getInfoLabel('ListItem.Property(Artist_Description)')
        if not text: text = xbmc.getInfoLabel('ListItem.Property(Album_Description)')
        if not text: text = xbmc.getInfoLabel('ListItem.Property(Addon.Description)')
        if not text: text = guitables.getSongInfo()
        if not text: text = parseItemExtra(controlID,self.getControlText(controlID)[0])
        if not text: return None
        if not isinstance(text,(list,tuple)): text = [text]
        return text

class NullReader(WindowReaderBase):
    ID = 'null'
    def getName(self): return None

    def getControlText(self,controlID): return (u'',u'')

    def getWindowExtraTexts(self): return None

class KeymapKeyInputReader(NullReader):
    ID = 'keymapkeyinput'
    def getWindowTexts(self): return [util.T(32124)]
