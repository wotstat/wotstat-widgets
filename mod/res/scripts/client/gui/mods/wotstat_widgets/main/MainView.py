import BigWorld
import struct
from functools import partial
from Event import Event
from aih_constants import CTRL_MODE_NAME
from gui.Scaleform.framework import g_entitiesFactories, ScopeTemplates, ViewSettings
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.application import AppEntry
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from gui.shared.personality import ServicesLocator
from gui.app_loader.settings import APP_NAME_SPACE
from frameworks.wulf import WindowLayer
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
from skeletons.account_helpers.settings_core import ISettingsCore
from Avatar import PlayerAvatar
from AvatarInputHandler import AvatarInputHandler
from typing import Tuple

from ..common.Logger import Logger
from .CefServer import CefServer, server
from .ChangeUrlWindow import show as showChangeUrlWindow
from .WidgetStorage import LAYER, WidgetStorage, POSITION_MODE, WidgetInfo
from .WidgetManager import WidgetManager
from .WidgetContextMenu import WidgetContextMenuHandler, BUTTONS as CE
from .MainViewMeta import MainViewMeta

CEF_MAIN_VIEW = "WOTSTAT_CEF_MAIN_VIEW"

logger = Logger.instance()
storage = WidgetStorage.instance()
manager = WidgetManager.instance()

lastLoadIsBattle = False

class MainView(View, MainViewMeta):
  settingsCore = dependency.descriptor(ISettingsCore) # type: ISettingsCore
  
  def __init__(self, *args, **kwargs):
    super(MainView, self).__init__(*args, **kwargs)


def setup():
  WidgetContextMenuHandler.register()
  
  mainViewSettings = ViewSettings(
    CEF_MAIN_VIEW,
    MainView,
    "wotstat.widgets.swf",
    WindowLayer.SERVICE_LAYOUT,
    None,
    ScopeTemplates.GLOBAL_SCOPE,
  )
  g_entitiesFactories.addSettings(mainViewSettings)


  def onAppInitialized(event):
    global lastLoadIsBattle
    logger.info("App initialized: %s" % event.ns)

    if event.ns == APP_NAME_SPACE.SF_LOBBY:

      app = ServicesLocator.appLoader.getApp(event.ns) # type: AppEntry
      if not app:
        logger.error("App not found")
        return

      uiLoader = dependency.instance(IGuiLoader) # type: IGuiLoader
      parent = uiLoader.windowsManager.getMainWindow() if uiLoader and uiLoader.windowsManager else None

      lastLoadIsBattle = False
      app.loadView(SFViewLoadParams(CEF_MAIN_VIEW, parent=parent))

    elif event.ns == APP_NAME_SPACE.SF_BATTLE:

      app = ServicesLocator.appLoader.getApp(event.ns) # type: AppEntry
      if not app:
        logger.error("App not found")
        return
      
      lastLoadIsBattle = True
      app.loadView(SFViewLoadParams(CEF_MAIN_VIEW))

  g_eventBus.addListener(events.AppLifeCycleEvent.INITIALIZED, onAppInitialized, EVENT_BUS_SCOPE.GLOBAL)
