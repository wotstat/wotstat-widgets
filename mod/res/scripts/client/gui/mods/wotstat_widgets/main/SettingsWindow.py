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
from ..constants import WOTSTAT_WIDGETS_EVENT_OPEN_SETTINGS, WIDGETS_COLLECTION_URL
from ..common.i18n import t

CEF_SETTINGS_WINDOW = "WOTSTAT_CEF_SETTINGS_WINDOW"

notifier = Notifier.instance()

class SettingsWindow(AbstractWindowView):

  def onWindowClose(self):
    self.destroy()
    
  def py_openWidgetsCollection(self):
    BigWorld.wg_openWebBrowser('https://wotstat.info/widgets')

  def py_openWidget(self, url):
    manager.createWidget(url, 300, -1)
    self.destroy()

  def py_openDemoWidget(self):
    manager.createWidget(WIDGETS_COLLECTION_URL + '/demo-widget', 300, -1)
    self.destroy()
    
  def py_openUnpackError(self):
    BigWorld.wg_openWebBrowser(WIDGETS_COLLECTION_URL + '/manual-install')
    
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
      self._as_setTextState(text_styles.main(t('settings.runtimeError')))
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

def setup():
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