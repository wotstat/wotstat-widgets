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
from skeletons.account_helpers.settings_core import ISettingsCore
import struct

from ..common.Logger import Logger
from .CefServer import CefServer, server
from .EventsManager import manager

CEF_MAIN_VIEW = "WOTSTAT_CEF_MAIN_VIEW"

logger = Logger.instance()
lastWidgetUUID = 0

class MainView(View):
  settingsCore = dependency.descriptor(ISettingsCore) # type: ISettingsCore

  widgetFlags = {}

  def __init__(self, *args, **kwargs):
    super(MainView, self).__init__(*args, **kwargs)

  def _populate(self):
    super(MainView, self)._populate()
    logger.info("MainView populated")
    manager.createWidget += self._createWidget
    server.onFrame += self._onFrame

    self.settingsCore.interfaceScale.onScaleChanged += self.setInterfaceScale
    self.setInterfaceScale()

  def _dispose(self):
    manager.createWidget -= self._createWidget
    server.onFrame -= self._onFrame
    self.settingsCore.interfaceScale.onScaleChanged -= self.setInterfaceScale
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
    self.widgetFlags.pop(uuid, None)

  def _createWidget(self, url, width, height=-1):
    global lastWidgetUUID
    lastWidgetUUID += 1
    server.createNewWidget(lastWidgetUUID, url, width, height)
    self._as_createWidget(lastWidgetUUID, url, width, height)

  def bytesToIntArray(self, data):
    # type: (bytes) -> list[int]

    numIntegers = len(data) // 4
    intArray = struct.unpack('!%sI' % numIntegers, data[:numIntegers*4])

    mod = len(data) % 4
    if mod > 0:
      shift = 4 - mod
      data += b'\x00' * shift

      intArray += struct.unpack('!I', data[numIntegers*4:])

    return (4 - mod if mod > 0 else 0, list(intArray))
  
  def _onFrame(self, uuid, flags, width, height, length, data):
    # type: (int, int, int, int, int, bytes) -> None
  
    (shift, int_array) = self.bytesToIntArray(data)
    self._as_onFrame(uuid, width, height, int_array, shift)

    oldFlags = self.widgetFlags.get(uuid, None)
    self.widgetFlags[uuid] = flags

    def isChanged(flag):
      return oldFlags is None or (oldFlags & flag) != (flags & flag)

    if isChanged(CefServer.Flags.AUTO_HEIGHT):
      logger.info("Resize mode changed: %s" % (flags & CefServer.Flags.AUTO_HEIGHT == 0))
      self._as_setResizeMode(uuid, flags & CefServer.Flags.AUTO_HEIGHT == 0)
      
  def setInterfaceScale(self, scale=None):
    if not scale:
      scale = self.settingsCore.interfaceScale.get()
    self._as_setInterfaceScale(scale)

  def _as_onFrame(self, uuid, width, height, data, shift):
    self.flashObject.as_onFrame(uuid, width, height, data, shift)

  def _as_createWidget(self, uuid, url, width, height):
    self.flashObject.as_createWidget(uuid, url, width, height)

  def _as_setResizeMode(self, uuid, mode):
    self.flashObject.as_setResizeMode(uuid, mode)

  def _as_setInterfaceScale(self, scale):
    self.flashObject.as_setInterfaceScale(scale)



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
