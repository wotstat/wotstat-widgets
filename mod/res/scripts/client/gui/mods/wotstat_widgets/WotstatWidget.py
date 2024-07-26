import os
import zipfile

import BigWorld
from gui import SystemMessages
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.shared.utils import IHangarSpace

from .common.ServerLoggerBackend import ServerLoggerBackend
from .common.Logger import Logger, SimpleLoggerBackend
from .common.Config import Config
from .common.utils import copyFile
from .main.MainView import setup as mainViewSetup
from .main.SettingsWindow import setup as settingsWindowSetup, show as showSettingsWindow
from .main.CefServer import server
from .common.Notifier import Notifier
from .common.i18n import t

from .constants import CEF_PATH, CONFIG_PATH, WOTSTAT_WIDGETS_EVENT_OPEN_SETTINGS

DEBUG_MODE = '{{DEBUG_MODE}}'

logger = Logger.instance()
notifier = Notifier.instance()

def copyCef():
  logger.info("Copy CEF to %s" % CEF_PATH)
  copyFile('wotstat.widgets.cef.zip', 'mods/wotstat.widgets.cef.zip')
  zipfile.ZipFile('mods/wotstat.widgets.cef.zip').extractall('mods')
  os.remove('mods/wotstat.widgets.cef.zip')


class WotstatWidget(object):
  
  def __init__(self):
    self.afterConnected = False
    
    logger.info("Starting WotStatWidget")

    self.config = Config(CONFIG_PATH)

    version = self.config.get("version")
    logger.info("Config loaded. Version: %s" % version)

    logger.setup([
      SimpleLoggerBackend(prefix="[MOD_WOTSTAT_WIDGET]", minLevel="INFO" if not DEBUG_MODE else "DEBUG"),
      ServerLoggerBackend(url=self.config.get('lokiURL'),
                          prefix="[MOD_WOTSTAT_WIDGET]",
                          source="mod_widget",
                          modVersion=version,
                          minLevel="INFO")
    ])

    copyCef()
    server.enable(self.config.get('devtools'))
    mainViewSetup()
    settingsWindowSetup()
    
    self.setupModListApi()
    
    hangarSpace = dependency.instance(IHangarSpace) # type: IHangarSpace
    connectionMgr = dependency.instance(IConnectionManager) # type: IConnectionManager
    
    connectionMgr.onConnected += self.onConnected
    hangarSpace.onSpaceCreate += self.onHangarLoaded
    
    logger.info("WotStatWidget started")

  def fini(self):
    logger.info("Stopping WotStatWidget")
    server.dispose()
    
  def onConnected(self, *a, **k):
    self.afterConnected = True
    
  def onHangarLoaded(self, *a, **k):
    if not self.afterConnected: return
    self.afterConnected = False
    
    if self.hasModListApi():
      return
    
    notifier.showNotification(t('notification.addWidget') % WOTSTAT_WIDGETS_EVENT_OPEN_SETTINGS, SystemMessages.SM_TYPE.InformationHeader,  messageData={'header': t('notification.addWidget.header')})

  def hasModListApi(self):
    try:
      from gui.modsListApi import g_modsListApi
      return True
    except:
      return False
    
  def setupModListApi(self):
    try:
      from gui.modsListApi import g_modsListApi

      def callback():
        showSettingsWindow()

      g_modsListApi.addModification(
        id="wotstat_widgets",
        name=t('modslist.title'),
        description=t('modslist.description'),
        icon='gui/maps/wotstat.widgets/modsListApi.png',
        enabled=True,
        login=False,
        lobby=True,
        callback=callback
      )
      
      return True
    except:
      return False

