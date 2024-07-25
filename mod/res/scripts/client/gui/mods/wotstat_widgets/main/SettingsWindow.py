import BigWorld
from frameworks.wulf.gui_constants import WindowLayer
from gui.Scaleform.framework import g_entitiesFactories, ScopeTemplates, ViewSettings
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from gui.Scaleform.framework.application import AppEntry

from .EventsManager import manager
from ..common.Notifier import Notifier
from ..constants import WOTSTAT_WIDGETS_EVENT_OPEN_SETTINGS
from ..common.i18n import t

CEF_SETTINGS_WINDOW = "WOTSTAT_CEF_SETTINGS_WINDOW"

notifier = Notifier.instance()

class SettingsWindow(AbstractWindowView):

  def onWindowClose(self):
    self.destroy()
    
  def py_openWidgetsCollection(self):
    BigWorld.wg_openWebBrowser("https://wotstat.info/widgets")

  def py_openWidget(self, url):
    manager.createWidget(url, 300, -1)
    self.destroy()

  def py_openDemoWidget(self):
    manager.createWidget('https://wotstat.info/widgets/demo', 300, -1)
    self.destroy()
    
  def py_t(self, key):
    return t(key)

def setup():
  settingsViewSettings = ViewSettings(
    CEF_SETTINGS_WINDOW,
    SettingsWindow,
    "wotstat.widgets.settings.swf",
    WindowLayer.WINDOW,
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