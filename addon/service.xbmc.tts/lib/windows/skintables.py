# -*- coding: utf-8 -*-
import xbmcvfs
import xbmc
from lib import util
quartz = {    10000:
            {    301:{'name':20342,'prefix':util.T(32175)}, #Movies
                302:{'name':20343,'prefix':util.T(32175)}, #TV Shows
                303:{'name':2,'prefix':util.T(32175)}, #Music
                304:{'name':1,'prefix':util.T(32175)}, #Pictures
                305:{'name':24001,'prefix':util.T(32175)}, #Addons
                306:{'name':'X B M C','prefix':util.T(32175)},
                312:{'name':20387,'prefix':util.T(32176)}, #Recently added tv shows
                313:{'name':359,'prefix':util.T(32176)}, #Recently added albums
            }

}

skins = {    'quartz': quartz
}

CURRENT_SKIN_TABLE = None
CURRENT_SKIN = None

def getSkinName():
    """Return the active skin id without the ``skin.`` prefix.

    Kodi can change skins without restarting the service.  Keeping this
    lookup separate lets window dispatch refresh skin-specific readers when
    that happens instead of retaining the skin that was active at import.
    """
    import os
    skinPath = xbmcvfs.translatePath('special://skin')
    return os.path.basename(skinPath.rstrip(r'\/')).split('skin.',1)[-1]

def getControlText(winID,controlID):
    table = CURRENT_SKIN_TABLE
    if not table: return 
    if not  winID in table: return
    if not controlID in table[winID]: return
    label = table[winID][controlID]['name']
    if isinstance(label,int): label = xbmc.getLocalizedString(label)
    if not label: return
    if not 'prefix' in table[winID][controlID]: return label
    return u'{0}: {1}'.format(table[winID][controlID]['prefix'],label)


def getSkinTable():
    global CURRENT_SKIN
    skinName = getSkinName()
    CURRENT_SKIN = skinName
    print('service.xbmc.tts: SKIN: %s' % skinName)
    return skins.get(skinName)

def updateSkinTable():
    global CURRENT_SKIN_TABLE
    CURRENT_SKIN_TABLE = getSkinTable()
    
updateSkinTable()
