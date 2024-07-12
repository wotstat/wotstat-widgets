import BigWorld
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
import base64

from ..common.Logger import Logger
from .CefServer import server
from .EventsManager import manager

CEF_MAIN_VIEW = "WOTSTAT_CEF_MAIN_VIEW"

logger = Logger.instance()
lastWidgetUUID = 0

class MainView(View):
  def __init__(self, *args, **kwargs):
    super(MainView, self).__init__(*args, **kwargs)

  def _populate(self):
    super(MainView, self)._populate()
    logger.info("MainView populated")
    manager.createWidget += self._createWidget
    server.onFrame += self._onFrame

  def _dispose(self):
    manager.createWidget -= self._createWidget
    server.onFrame -= self._onFrame
    logger.info("MainView disposed")
    super(MainView, self)._dispose()

  def py_log(self, msg, level):
    logger.printLog(level, msg)

  def py_requestResize(self, uuid, width, height):
    server.resizeWidget(uuid, width, height)

  def py_requestReload(self, uuid):
    server.reloadWidget(uuid)

  def py_requestClose(self, uuid):
    server.closeWidget(uuid)

  def _createWidget(self, url, width, height=-1):
    global lastWidgetUUID
    lastWidgetUUID += 1
    server.createNewWidget(lastWidgetUUID, url, width, height)
    self.flashObject.as_createWidget(lastWidgetUUID, url, width, height)

  def _onFrame(self, uuid, width, height, length, data):
    self.flashObject.as_onFrame(uuid, width, height, base64.b64encode(data).decode('utf-8'))


def setup():
  mainViewSettings = ViewSettings(
    CEF_MAIN_VIEW,
    MainView,
    "wotstat.cef.swf",
    WindowLayer.WINDOW,
    None,
    ScopeTemplates.GLOBAL_SCOPE,
  )
  g_entitiesFactories.addSettings(mainViewSettings)


  def onAppInitialized(event):
    if event.ns == APP_NAME_SPACE.SF_LOBBY:
      logger.info("SF_LOBBY initialized")

      app = ServicesLocator.appLoader.getApp(event.ns)  # type: AppEntry
      if not app:
        logger.error("App not found")
        return

      uiLoader = dependency.instance(IGuiLoader)  # type: IGuiLoader
      parent = uiLoader.windowsManager.getMainWindow() if uiLoader and uiLoader.windowsManager else None
      app.loadView(SFViewLoadParams(CEF_MAIN_VIEW, parent=parent))

  g_eventBus.addListener(events.AppLifeCycleEvent.INITIALIZED, onAppInitialized, EVENT_BUS_SCOPE.GLOBAL)
