# -*- coding: utf-8 -*-
from .base import WindowReaderBase
import xbmc
from lib import util

class SettingsReader(WindowReaderBase):
    ID = 'settings'

    def getWindowExtraTexts(self):
        return None

    def getItemExtraTexts(self,controlID):
        text = xbmc.getInfoLabel('Container({0}).ListItem.Label2'.format(controlID))
        if not text: return None
        return [text]

    def getControlText(self,controlID):
        if not controlID: return (u'',u'')
        sub = u''
        raw = xbmc.getInfoLabel('System.CurrentControl')
        text = self.getSettingControlText(controlID)
        if text.startswith('-'): sub = u'{0}: '.format(util.T(32172))
        role = u''
        if getattr(self.service, 'speakControlRoles', True):
            if '(*)' in raw or '( )' in raw:
                role = u', {0}'.format(util.T(32234))
            else:
                role = u', {0}'.format(util.T(32235))
        spoken = u'{0}{1}{2}'.format(sub,text,role)
        identity = u'{0}\x1f{1}\x1f{2}'.format(self.winID, controlID, raw)
        return (spoken,identity)
