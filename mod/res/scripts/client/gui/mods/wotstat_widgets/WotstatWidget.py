import os
import zipfile

import BigWorld
from gui import SystemMessages
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.shared.utils import IHangarSpace

from .CefArchive import cefArchive
from .common.ServerLoggerBackend import ServerLoggerBackend
from .common.Logger import Logger, SimpleLoggerBackend
from .common.Config import Config
from .main.MainView import setup as mainViewSetup
from .main.SettingsWindow import setup as settingsWindowSetup, show as showSettingsWindow
from .main.ChangeUrlWindow import setup as changeUrlWindowSetup
from .main.CefServer import server
from .main.WebSocketInterface import WebSocketInterface
from .common.Notifier import Notifier
from .common.i18n import t
from .common.ModUpdater import ModUpdater
from .dataProvider import setup as setupDataProvider


from .constants import CEF_PATH, CONFIG_PATH, WOTSTAT_WIDGETS_EVENT_OPEN_SETTINGS, GITHUB_URL

DEBUG_MODE = '{{DEBUG_MODE}}'
CEF_SERVER_CHECKSUM = '{{CEF_SERVER_CHECKSUM}}'

logger = Logger.instance()
notifier = Notifier.instance()

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

    cefArchive.onReady += self.onCefArchiveReady
    cefArchive.setup(CEF_SERVER_CHECKSUM)
    mainViewSetup()
    settingsWindowSetup()
    changeUrlWindowSetup()
    
    self.setupModListApi()
    self.checkAndUpdate(version)
    
    self.wsInterface = WebSocketInterface()
    self.wsInterface.setup()
    
    hangarSpace = dependency.instance(IHangarSpace) # type: IHangarSpace
    connectionMgr = dependency.instance(IConnectionManager) # type: IConnectionManager
    
    connectionMgr.onConnected += self.onConnected
    hangarSpace.onSpaceCreate += self.onHangarLoaded
    
    logger.info("WotStatWidget started")
    
    setupDataProvider(logger)

  def onCefArchiveReady(self):
    cefArchive.onReady -= self.onCefArchiveReady
    server.enable(self.config.get('devtools'))

  def fini(self):
    logger.info("Stopping WotStatWidget")
    server.dispose()
    cefArchive.dispose()
    self.wsInterface.dispose()
    logger.info('WotStatWidget stopped')
    
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

  def checkAndUpdate(self, currentVersion):
    updater = ModUpdater(modName="wotstat.widgets",
                      currentVersion=currentVersion,
                      ghUrl=GITHUB_URL)
    updater.updateToGitHubReleases(lambda status: logger.info("Update status: %s" % status))