import BigWorld
from gui.Scaleform.framework import g_entitiesFactories, ScopeTemplates, ViewSettings
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.application import AppEntry
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from gui.shared.personality import ServicesLocator
from gui.app_loader.settings import APP_NAME_SPACE
from gui import InputHandler
from frameworks.wulf import WindowLayer
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
from skeletons.account_helpers.settings_core import ISettingsCore
import struct
import Keys

from ..common.Logger import Logger
from .CefServer import CefServer, server
from .EventsManager import manager
from .WidgetStorage import WidgetStorage

CEF_MAIN_VIEW = "WOTSTAT_CEF_MAIN_VIEW"

logger = Logger.instance()
storage = WidgetStorage.instance()
lastWidgetId = 0
lastLoadIsBattle = False

class MainView(View):
  settingsCore = dependency.descriptor(ISettingsCore) # type: ISettingsCore
  controlPressed = False

  def __init__(self, *args, **kwargs):
    super(MainView, self).__init__(*args, **kwargs)

  def _populate(self):
    super(MainView, self)._populate()
    logger.info("MainView populated")
    manager.createWidget += self._createWidget
    server.onFrame += self._onFrame

    InputHandler.g_instance.onKeyDown += self._onKey
    InputHandler.g_instance.onKeyUp += self._onKey

    self.settingsCore.interfaceScale.onScaleChanged += self.setInterfaceScale
    self.setInterfaceScale()

    for widget in storage.getAllWidgets():
      self._addWidget(widget.uuid, widget.wid, widget.url, widget.width, widget.height, widget.x, widget.y, widget.flags, widget.isHidden, widget.isLocked)
      server.redrawWidget(widget.wid)

  def _dispose(self):
    manager.createWidget -= self._createWidget
    server.onFrame -= self._onFrame
    self.settingsCore.interfaceScale.onScaleChanged -= self.setInterfaceScale

    InputHandler.g_instance.onKeyDown -= self._onKey
    InputHandler.g_instance.onKeyUp -= self._onKey

    logger.info("MainView disposed")
    super(MainView, self)._dispose()

  def _onKey(self, event):
    # type: (BigWorld.KeyEvent) -> None

    if event.key in (Keys.KEY_LCONTROL, Keys.KEY_RCONTROL):

      if self.controlPressed != event.isKeyDown():
        self.controlPressed = event.isKeyDown()
        self._as_setControlPressed(self.controlPressed)

  def py_log(self, msg, level):
    logger.printLog(level, msg)

  def py_moveWidget(self, wid, x, y):
    storage.updateWidget(wid, x=x, y=y)

  def py_lockUnlockWidget(self, wid, isLocked):
    storage.updateWidget(wid, isLocked=isLocked)

  def py_hideShowWidget(self, wid, isHidden):
    storage.updateWidget(wid, isHidden=isHidden)

  def py_requestResize(self, wid, width, height):
    server.resizeWidget(wid, width, height)
    storage.updateWidget(wid, width=width, height=height)

  def py_requestReload(self, wid):
    server.reloadWidget(wid)

  def py_requestClose(self, wid):
    server.closeWidget(wid)
    storage.removeWidget(wid)

  def getNextWidgetId(self):
    global lastWidgetId
    lastWidgetId += 1
    return lastWidgetId

  def _addWidget(self, uuid, wid, url, width=100, height=100, x=-1, y=-1, flags=0, isHidden=False, isLocked=False):
    if wid:
      self._as_createWidget(wid, url, width, height, x, y, isHidden, isLocked, lastLoadIsBattle)
    else:
      wid = self.getNextWidgetId()
      storage.setWidgetWid(uuid, wid)

      server.createNewWidget(wid, url, width, height)
      self._as_createWidget(wid, url, width, height, x, y, isHidden, isLocked, lastLoadIsBattle)

    self._as_setResizeMode(wid, flags & CefServer.Flags.AUTO_HEIGHT == 0)

  def _createWidget(self, url, width, height=-1):
    wid = self.getNextWidgetId()
    storage.addWidget(wid, url, width, height)
    server.createNewWidget(wid, url, width, height)
    self._as_createWidget(wid, url, width, height, isInBattle=lastLoadIsBattle)
    self._as_setResizeMode(wid, True)

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
  
  def _onFrame(self, wid, flags, width, height, length, data):
    # type: (int, int, int, int, int, bytes) -> None

    (shift, int_array) = self.bytesToIntArray(data)
    self._as_onFrame(wid, width, height, int_array, shift)

    oldFlags = storage.getWidgetFlags(wid)
    if oldFlags != flags:
      storage.updateWidget(wid, flags=flags)

      def isChanged(flag):
        return oldFlags is None or (oldFlags & flag) != (flags & flag)

      if isChanged(CefServer.Flags.AUTO_HEIGHT):
        logger.info("Resize mode changed: %s" % (flags & CefServer.Flags.AUTO_HEIGHT == 0))
        self._as_setResizeMode(wid, flags & CefServer.Flags.AUTO_HEIGHT == 0)
      
  def setInterfaceScale(self, scale=None):
    if not scale:
      scale = self.settingsCore.interfaceScale.get()
    self._as_setInterfaceScale(scale)

  def _as_onFrame(self, wid, width, height, data, shift):
    self.flashObject.as_onFrame(wid, width, height, data, shift)

  def _as_createWidget(self, wid, url, width, height, x=-1, y=-1, isHidden=False, isLocked=False, isInBattle=False):
    self.flashObject.as_createWidget(wid, url, width, height, x, y, isHidden, isLocked, isInBattle)

  def _as_setResizeMode(self, wid, mode):
    self.flashObject.as_setResizeMode(wid, mode)

  def _as_setInterfaceScale(self, scale):
    self.flashObject.as_setInterfaceScale(scale)

  def _as_setControlPressed(self, pressed):
    self.flashObject.as_setControlPressed(pressed)



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
    global lastLoadIsBattle
    logger.info("App initialized: %s" % event.ns)

    if event.ns == APP_NAME_SPACE.SF_LOBBY:
      logger.info("SF_LOBBY initialized")

      app = ServicesLocator.appLoader.getApp(event.ns)  # type: AppEntry
      if not app:
        logger.error("App not found")
        return

      uiLoader = dependency.instance(IGuiLoader)  # type: IGuiLoader
      parent = uiLoader.windowsManager.getMainWindow() if uiLoader and uiLoader.windowsManager else None

      lastLoadIsBattle = False
      app.loadView(SFViewLoadParams(CEF_MAIN_VIEW, parent=parent))

    elif event.ns == APP_NAME_SPACE.SF_BATTLE:
      logger.info("SF_BATTLE initialized")

      app = ServicesLocator.appLoader.getApp(event.ns)  # type: AppEntry
      if not app:
        logger.error("App not found")
        return
      
      lastLoadIsBattle = True
      app.loadView(SFViewLoadParams(CEF_MAIN_VIEW))

  g_eventBus.addListener(events.AppLifeCycleEvent.INITIALIZED, onAppInitialized, EVENT_BUS_SCOPE.GLOBAL)
