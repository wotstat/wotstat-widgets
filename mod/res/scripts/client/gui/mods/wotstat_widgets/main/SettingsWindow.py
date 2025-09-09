import BigWorld
from frameworks.wulf.gui_constants import WindowLayer
from gui.Scaleform.framework import g_entitiesFactories, ScopeTemplates, ViewSettings
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from gui.Scaleform.framework.application import AppEntry
from gui.shared.formatters import text_styles

from .EventsManager import manager
from .CefServer import server
from ..CefArchive import cefArchive
from ..common.Notifier import Notifier
from ..common.Logger import Logger
from ..constants import WOTSTAT_WIDGETS_EVENT_OPEN_SETTINGS, WIDGETS_COLLECTION_URL, WIDGETS_COLLECTION_URL_RU
from ..common.i18n import t

CEF_SETTINGS_WINDOW = "WOTSTAT_CEF_SETTINGS_WINDOW"

openWebBrowser = BigWorld.wg_openWebBrowser if hasattr(BigWorld, 'wg_openWebBrowser') else BigWorld.openWebBrowser
notifier = Notifier.instance()
logger = Logger.instance()

preferredRuBackend = False

def checkBackendAvailability():
  def onResponse(response):
    global preferredRuBackend
    if response is None or response.responseCode != 200:
      preferredRuBackend = True
      logger.info('Cannot reach global backend, using RU backend')
    else:
      preferredRuBackend = False
      logger.info('Global backend is reachable, using it')

  logger.info('Checking global backend availability...')
  BigWorld.fetchURL(WIDGETS_COLLECTION_URL, onResponse, timeout=5)
  

class SettingsWindow(AbstractWindowView):

  def onWindowClose(self):
    self.destroy()

  def collectionUrl(self):
    return WIDGETS_COLLECTION_URL_RU if preferredRuBackend else WIDGETS_COLLECTION_URL
    
  def py_openWidgetsCollection(self):
    openWebBrowser(self.collectionUrl())

  def py_openWidget(self, url):
    manager.createWidget(url, 300, -1)
    self.destroy()

  def py_openDemoWidget(self):
    manager.createWidget(self.collectionUrl() + '/demo-widget', 300, -1)
    self.destroy()
    
  def py_openUnpackError(self):
    openWebBrowser(self.collectionUrl() + '/manual-install')

  def py_openRuntimeError(self):
    openWebBrowser(self.collectionUrl() + '/common-issues')
    
  def py_t(self, key):
    return t(key)
  
  def _populate(self):
    super(SettingsWindow, self)._populate()
    self.isWaitingForCef = False
    
    server.onProcessError += self._onCefRuntimeError
    
    if not cefArchive.isReady:
      self.isWaitingForCef = True
      cefArchive.onReady += self._onCefServerReady
      cefArchive.onProgressChange += self._onCefProgressChange
      cefArchive.onError += self._onCefError
      
    self._updateState()
  
  def _dispose(self):
    if self.isWaitingForCef:
      cefArchive.onReady -= self._onCefServerReady
      cefArchive.onProgressChange -= self._onCefProgressChange
      cefArchive.onError -= self._onCefError
      
    server.onProcessError -= self._onCefRuntimeError
    super(SettingsWindow, self)._dispose()
    return
        
  def _onCefServerReady(self):
    self._updateState()
    self.isWaitingForCef = False
    cefArchive.onReady -= self._onCefServerReady
    cefArchive.onProgressChange -= self._onCefProgressChange
    cefArchive.onError -= self._onCefError
    
  def _onCefProgressChange(self, progress):
    self._updateState()

  def _onCefError(self, error):
    self._updateState()
  
  def _onCefRuntimeError(self, error):
    self._updateState()
  
  def _updateState(self):
    if server.hasProcessError:
      self._as_setTextState(str().join((
        text_styles.main(t('settings.runtimeError')),
        '\n\n',
        text_styles.main(t('settings.error')),
        text_styles.error(str(server.lastProcessError)),
        '\n\n',
        text_styles.main(t('settings.runtimeErrorContact')),
      )))
      self._as_showRuntimeErrorButton()
      return
    
    if cefArchive.isReady:
      self._as_setNormalState()
      return
    
    hasError = cefArchive.lastError is not None
    formattedProgress = str(round(cefArchive.progress * 1000)/10) + '%'
    if cefArchive.progress > 1: formattedProgress = t('settings.unpackingProcess')
    
    if cefArchive.progress == -2:
      self._as_setTextState(text_styles.main(t('settings.platformNotSupported') % cefArchive.machine))
      
    elif hasError and cefArchive.progress == -1:
      self._as_setTextState(str().join((
        text_styles.main(t('settings.cannotUnpack')),
        '\n\n',
        text_styles.main(t('settings.error')),
        text_styles.main(str(cefArchive.lastError)),
      )))
      self._as_showUnpackErrorButton()
      
    elif hasError:
      self._as_setTextState(str().join((
        text_styles.main(t('settings.needUnpack')),
        '\n\n<b>',
        text_styles.main(t('settings.retrying') % (str(cefArchive.retryCount+1), formattedProgress)),
        '</b>\n\n',
        text_styles.main(t('settings.error')),
        text_styles.main(str(cefArchive.lastError)),
      )))
      
    else:
      self._as_setTextState(str().join((
        text_styles.main(t('settings.needUnpack')),
        '\n\n',
        text_styles.main(t('settings.pleaseWait')),
        '\n\n<b>',
        text_styles.main(t('settings.downloading') % formattedProgress),
        '</b>'
      )))

  def _as_setNormalState(self):
    self.flashObject.as_setNormalState()
    
  def _as_setTextState(self, text):
    self.flashObject.as_setTextState(text)
    
  def _as_showUnpackErrorButton(self):
    self.flashObject.as_showUnpackErrorButton()
    
  def _as_showRuntimeErrorButton(self):
    self.flashObject.as_showRuntimeErrorButton()

def setup():
  checkBackendAvailability()

  settingsViewSettings = ViewSettings(
    CEF_SETTINGS_WINDOW,
    SettingsWindow,
    "wotstat.widgets.settings.swf",
    WindowLayer.TOP_WINDOW,
    None,
    ScopeTemplates.VIEW_SCOPE,
  )
  g_entitiesFactories.addSettings(settingsViewSettings)
  
  def onEvent(event):
    if event == WOTSTAT_WIDGETS_EVENT_OPEN_SETTINGS:
      show()
      
  notifier.onEvent += onEvent
  

def show():
  appLoader = dependency.instance(IAppLoader) # type: IAppLoader
  app = appLoader.getApp() # type: AppEntry
  app.loadView(SFViewLoadParams(CEF_SETTINGS_WINDOW))