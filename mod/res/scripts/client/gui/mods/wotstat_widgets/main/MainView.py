import BigWorld
from Event import Event
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
from .WidgetContextMenu import WidgetContextMenuHandler, BUTTONS as CE
from skeletons.gui.impl import IGuiLoader
from skeletons.account_helpers.settings_core import ISettingsCore
from Avatar import PlayerAvatar
from AvatarInputHandler import AvatarInputHandler
import struct
import Keys

from ..common.Logger import Logger
from .CefServer import CefServer, server
from .EventsManager import manager
from .ChangeUrlWindow import show as showChangeUrlWindow
from .WidgetStorage import WidgetStorage

CEF_MAIN_VIEW = "WOTSTAT_CEF_MAIN_VIEW"

logger = Logger.instance()
storage = WidgetStorage.instance()
lastWidgetId = 0
lastLoadIsBattle = False

class MainView(View):
  settingsCore = dependency.descriptor(ISettingsCore) # type: ISettingsCore
  controlPressed = False
  isOnSetupSubscribed = False

  def __init__(self, *args, **kwargs):
    super(MainView, self).__init__(*args, **kwargs)

  def _populate(self):
    super(MainView, self)._populate()
    logger.info("MainView populated")
    manager.createWidgetEvent += self._createWidget
    manager.changeUrlEvent += self._changeUrl
    server.onFrame += self._onFrame
    server.onProcessError += self._onServerError

    InputHandler.g_instance.onKeyDown += self._onKey
    InputHandler.g_instance.onKeyUp += self._onKey
    WidgetContextMenuHandler.onEvent += self._onWidgetContextEvent
    g_eventBus.addListener(events.GameEvent.FULL_STATS, self._handleToggleFullStats, scope=EVENT_BUS_SCOPE.BATTLE)
    g_eventBus.addListener(events.GameEvent.FULL_STATS_QUEST_PROGRESS, self._handleToggleFullStats, scope=EVENT_BUS_SCOPE.BATTLE)
    g_eventBus.addListener(events.GameEvent.FULL_STATS_PERSONAL_RESERVES, self._handleToggleFullStats, scope=EVENT_BUS_SCOPE.BATTLE)
    
    global onStartGUI, onControlModeChanged
    onStartGUI += self._onStartGUI
    onControlModeChanged += self._onControlModeChanged

    self.settingsCore.interfaceScale.onScaleChanged += self.setInterfaceScale
    self.setInterfaceScale()
    
    if server.isReady:
      self.addWidgets()
    else:
      server.onSetupComplete += self.onSetupComplete
      self.isOnSetupSubscribed = True

  def onSetupComplete(self):
    self.addWidgets()
    server.onSetupComplete -= self.onSetupComplete
    self.isOnSetupSubscribed = False
    
  def addWidgets(self):
    for widget in storage.getAllWidgets():
      if lastLoadIsBattle and widget.flags & CefServer.Flags.HANGAR_ONLY != 0:
        server.suspenseWidget(widget.wid)
        continue
      
      state = widget.battle if lastLoadIsBattle else widget.hangar
      oppositeState = widget.hangar if lastLoadIsBattle else widget.battle
      positionState = oppositeState if oppositeState.isTouched and not state.isTouched else state
      
      self._addWidget(widget.uuid, widget.wid, widget.url, positionState.width, positionState.height, positionState.x, positionState.y, widget.flags, state.isHidden, state.isLocked, state.isControlsAlwaysHidden)
      if state.isHidden:
        server.suspenseWidget(widget.wid)
      else:
        server.resumeWidget(widget.wid)
        
      server.redrawWidget(widget.wid)
      server.resizeWidget(widget.wid, positionState.width, positionState.height)
    
  def _dispose(self):
    manager.createWidgetEvent -= self._createWidget
    server.onFrame -= self._onFrame
    self.settingsCore.interfaceScale.onScaleChanged -= self.setInterfaceScale
    
    InputHandler.g_instance.onKeyDown -= self._onKey
    InputHandler.g_instance.onKeyUp -= self._onKey
    WidgetContextMenuHandler.onEvent -= self._onWidgetContextEvent
    g_eventBus.removeListener(events.GameEvent.FULL_STATS, self._handleToggleFullStats, scope=EVENT_BUS_SCOPE.BATTLE)
    g_eventBus.removeListener(events.GameEvent.FULL_STATS_QUEST_PROGRESS, self._handleToggleFullStats, scope=EVENT_BUS_SCOPE.BATTLE)
    g_eventBus.removeListener(events.GameEvent.FULL_STATS_PERSONAL_RESERVES, self._handleToggleFullStats, scope=EVENT_BUS_SCOPE.BATTLE)
    
    if self.isOnSetupSubscribed:
      server.onSetupComplete -= self.onSetupComplete

    global onStartGUI, onControlModeChanged
    onStartGUI -= self._onStartGUI
    onControlModeChanged -= self._onControlModeChanged

    logger.info("MainView disposed")
    super(MainView, self)._dispose()

  def _onKey(self, event):
    # type: (BigWorld.KeyEvent) -> None

    if event.key in (Keys.KEY_LCONTROL, Keys.KEY_RCONTROL):
      if self.controlPressed != event.isKeyDown():
        self.controlPressed = event.isKeyDown()
        self._as_setControlPressed(self.controlPressed)
    
  def _handleToggleFullStats(self, event):
    self._as_setGlobalVisible(not event.ctx.get('isDown', False))
    
  def _onStartGUI(self, *a, **k):
    self._as_setGlobalVisible(True)

  def _onControlModeChanged(self, *a, **k):
    player = BigWorld.player()
    if player is None: return
    if not hasattr(player, 'inputHandler'): return
    if not hasattr(player.inputHandler, 'ctrlModeName'): return
    
    ctrlModeName = player.inputHandler.ctrlModeName
    
    logger.info("Control mode changed: " + str(ctrlModeName))

  def _onWidgetContextEvent(self, event):
    eventName, wid = event
    logger.info("Widget context event[%d]: %s" % (wid, eventName))
    
    if eventName == CE.LOCK or eventName == CE.UNLOCK:
      target = eventName == CE.LOCK
      storage.updateWidget(wid, lastLoadIsBattle, isLocked=target)
      self._as_setLocked(wid, target)
      
    elif eventName == CE.RESIZE or eventName == CE.END_RESIZE:
      self._as_setResizing(wid, eventName == CE.RESIZE)
      
    elif eventName == CE.RELOAD:
      self.reloadWidget(wid)
      
    elif eventName == CE.REMOVE:
      self.closeWidget(wid)
      
    elif eventName == CE.CHANGE_URL:
      widget = storage.getWidgetByWid(wid)
      if widget:
        showChangeUrlWindow(wid, widget.url)
      else:
        logger.error("Widget [%s] not found" % str(wid))
      
    elif eventName == CE.HIDE_CONTROLS or eventName == CE.SHOW_CONTROLS:
      target = eventName == CE.HIDE_CONTROLS
      storage.updateWidget(wid, lastLoadIsBattle, isControlsAlwaysHidden=target)
      self._as_setControlsAlwaysHidden(wid, target)
      
    elif eventName == CE.CLEAR_DATA:
      server.sendWidgetCommand(wid, "CLEAR_DATA")
    
    elif eventName == CE.SEND_TO_TOP_LAYER:
      self._as_sendToTopLayer(wid)
  
    else:
      logger.error("Unknown context event: %s" % eventName)
      
  def closeWidget(self, wid):
    server.closeWidget(wid)
    storage.removeWidget(wid)
    self._as_closeWidget(wid)
  
  def reloadWidget(self, wid):
    server.reloadWidget(wid)

  def py_log(self, msg, level):
    logger.printLog(level, msg)

  def py_moveWidget(self, wid, x, y):
    storage.updateWidget(wid, lastLoadIsBattle, x=x, y=y)

  def py_lockUnlockWidget(self, wid, isLocked):
    storage.updateWidget(wid, lastLoadIsBattle, isLocked=isLocked)

  def py_hideShowWidget(self, wid, isHidden):
    storage.updateWidget(wid, lastLoadIsBattle, isHidden=isHidden)
    if isHidden:
      server.suspenseWidget(wid)
    else:
      server.resumeWidget(wid)
      server.redrawWidget(wid)

  def py_requestResize(self, wid, width, height):
    server.resizeWidget(wid, width, height)
    storage.updateWidget(wid, lastLoadIsBattle, width=width, height=height)

  def getNextWidgetId(self):
    global lastWidgetId
    lastWidgetId += 1
    return lastWidgetId

  def _onServerError(self, error):
    logger.info("Server error. Hide MainView: %s" % error)
    self._dispose()

  def _addWidget(self, uuid, wid, url, width=100, height=100, x=-1, y=-1, flags=0, isHidden=False, isLocked=False, isControlsAlwaysHidden=False):
    
    def create(wid):
      self._as_createWidget(wid, url, width, height, x, y, isHidden, isLocked, isControlsAlwaysHidden, lastLoadIsBattle)
      
    if wid:
      create(wid)
    else:
      wid = self.getNextWidgetId()
      storage.setWidgetWid(uuid, wid)

      server.createNewWidget(wid, url, width, height)
      create(wid)

    self._as_setResizeMode(wid, flags & CefServer.Flags.AUTO_HEIGHT == 0)
    self._as_setReadyToClearData(wid, not (flags & CefServer.Flags.READY_TO_CLEAR_DATA == 0))

  def _createWidget(self, url, width, height=-1):
    if not server.isReady:
      logger.error("CEF server is not ready")
      return
    
    wid = self.getNextWidgetId()
    storage.addWidget(wid, url, width, height)
    server.createNewWidget(wid, url, width, height)
    self._as_createWidget(wid, url, width, height, isInBattle=lastLoadIsBattle)
    self._as_setResizeMode(wid, True)

  def _changeUrl(self, wid, url):
    storage.updateWidget(wid, lastLoadIsBattle, url=url)
    server.changeWidgetUrl(wid, url)

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
      storage.updateWidget(wid, lastLoadIsBattle, flags=flags)

      def isChanged(flag):
        return oldFlags is None or (oldFlags & flag) != (flags & flag)

      if isChanged(CefServer.Flags.AUTO_HEIGHT):
        flag = flags & CefServer.Flags.AUTO_HEIGHT == 0
        logger.info("Resize mode changed: %s" % flag)
        self._as_setResizeMode(wid, flag)
        
      if isChanged(CefServer.Flags.READY_TO_CLEAR_DATA):
        flag = flags & CefServer.Flags.READY_TO_CLEAR_DATA == 0
        logger.info("Ready to clean changed: %s" % (not flag))
        self._as_setReadyToClearData(wid, not flag)
        
      if isChanged(CefServer.Flags.USE_SNIPER_MODE):
        flag = flags & CefServer.Flags.USE_SNIPER_MODE != 0
        logger.info("Use sniper mode changed: %s" % flag)
        
      if isChanged(CefServer.Flags.HANGAR_ONLY):
        flag = flags & CefServer.Flags.HANGAR_ONLY != 0
        logger.info("Hangar only changed: %s" % flag)
      
  def setInterfaceScale(self, scale=None):
    if not scale:
      scale = self.settingsCore.interfaceScale.get()
    self._as_setInterfaceScale(scale)

  def _as_onFrame(self, wid, width, height, data, shift):
    self.flashObject.as_onFrame(wid, width, height, data, shift)

  def _as_createWidget(self, wid, url, width, height, x=-1, y=-1,
                       isHidden=False, isLocked=False, isControlsAlwaysHidden=False, isInBattle=False):
    self.flashObject.as_createWidget(wid, url, width, height, x, y, isHidden, isLocked, isControlsAlwaysHidden, isInBattle)

  def _as_setResizeMode(self, wid, mode):
    self.flashObject.as_setResizeMode(wid, mode)
    
  def _as_setResizing(self, wid, enabled):
    self.flashObject.as_setResizing(wid, enabled)
    
  def _as_setLocked(self, wid, locked):
    self.flashObject.as_setLocked(wid, locked)
    
  def _as_setReadyToClearData(self, wid, ready):
    self.flashObject.as_setReadyToClearData(wid, ready)

  def _as_setControlsAlwaysHidden(self, wid, hidden):
    self.flashObject.as_setControlsAlwaysHidden(wid, hidden)

  def _as_sendToTopLayer(self, wid):
    self.flashObject.as_sendToTopLayer(wid)

  def _as_setInterfaceScale(self, scale):
    self.flashObject.as_setInterfaceScale(scale)

  def _as_setControlPressed(self, pressed):
    self.flashObject.as_setControlPressed(pressed)
    
  def _as_setGlobalVisible(self, visible):
    self.flashObject.as_setGlobalVisible(visible)

  def _as_closeWidget(self, wid):
    self.flashObject.as_closeWidget(wid)

onStartGUI = Event()
onControlModeChanged = Event()

oldStartGUI = PlayerAvatar._PlayerAvatar__startGUI
def startGUI(*a, **k):
  oldStartGUI(*a, **k)
  try:
    logger.info("Starting GUI")
    onStartGUI(*a, **k)
  except Exception as e:
    logger.error("Failed to start GUI")

PlayerAvatar._PlayerAvatar__startGUI = startGUI

oldOnControlModeChanged = AvatarInputHandler.onControlModeChanged
def controlModeChanged(*a, **k):
  oldOnControlModeChanged(*a, **k)
  try:
    onControlModeChanged(*a, **k)
  except Exception as e:
    logger.error("Failed to handle control mode change")

AvatarInputHandler.onControlModeChanged = controlModeChanged

def setup():
  WidgetContextMenuHandler.register()
  
  mainViewSettings = ViewSettings(
    CEF_MAIN_VIEW,
    MainView,
    "wotstat.widgets.swf",
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

      app = ServicesLocator.appLoader.getApp(event.ns) # type: AppEntry
      if not app:
        logger.error("App not found")
        return

      uiLoader = dependency.instance(IGuiLoader) # type: IGuiLoader
      parent = uiLoader.windowsManager.getMainWindow() if uiLoader and uiLoader.windowsManager else None

      lastLoadIsBattle = False
      app.loadView(SFViewLoadParams(CEF_MAIN_VIEW, parent=parent))

    elif event.ns == APP_NAME_SPACE.SF_BATTLE:
      logger.info("SF_BATTLE initialized")

      app = ServicesLocator.appLoader.getApp(event.ns) # type: AppEntry
      if not app:
        logger.error("App not found")
        return
      
      lastLoadIsBattle = True
      app.loadView(SFViewLoadParams(CEF_MAIN_VIEW))

  g_eventBus.addListener(events.AppLifeCycleEvent.INITIALIZED, onAppInitialized, EVENT_BUS_SCOPE.GLOBAL)
