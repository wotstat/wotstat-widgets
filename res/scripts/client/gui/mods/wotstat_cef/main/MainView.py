import subprocess
import threading

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

from ..common.Logger import Logger
from .constants import CEF_EXE_PATH
from .EventsManager import manager

CEF_MAIN_VIEW = "WOTSTAT_CEF_MAIN_VIEW"

class Commands:
  OPEN_NEW_BROWSER = 'OPEN_NEW_BROWSER'


logger = Logger.instance()


def readOutput(process):
  while True:
    output = process.stdout.readline()
    if output == b'' and process.poll() is not None:
      continue
    if output:
      print(output.decode().strip())

class MainView(View):

  def __init__(self, *args, **kwargs):
    super(MainView, self).__init__(*args, **kwargs)

    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE

    self.process = subprocess.Popen(CEF_EXE_PATH,
      startupinfo=startupinfo,
      stdin=subprocess.PIPE,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE)
    
    outputThread = threading.Thread(target=readOutput, args=(self.process,))
    outputThread.start()

  def sendTextInput(self, inputData):
    logger.info("Send input data: %s" % inputData)
    self.process.stdin.write(inputData)
    self.process.stdin.flush()
  
  def _populate(self):
    super(MainView, self)._populate()
    logger.info("MainView populated")
    manager.createWidget += self.__createWidget

  def _dispose(self):
    manager.createWidget -= self.__createWidget
    logger.info("MainView disposed")
    self.process.terminate()
    super(MainView, self)._dispose()

  def py_log(self, msg, level):
    logger.printLog(level, msg)

  def __createWidget(self, url, port, width, height):
    logger.info("Create widget: %s:%s" % (url, port))
    self.sendTextInput(Commands.OPEN_NEW_BROWSER + ' ' + url + ' ' + str(port) + ' ' + str(width) + ' ' + str(height) + '\n')
    self.flashObject.as_createWidget(url, port, width, height)


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
