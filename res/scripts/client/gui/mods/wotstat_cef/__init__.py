
import os

from gui.Scaleform.framework.application import AppEntry
from gui.app_loader.settings import APP_NAME_SPACE
from gui.Scaleform.framework import (
    g_entitiesFactories,
    ScopeTemplates,
    ViewSettings,
)
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.shared.personality import ServicesLocator
from frameworks.wulf import WindowLayer
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus

from helpers import dependency
from skeletons.gui.impl import IGuiLoader

from .views.MainView import MainView
import ResMgr

CEF_MAIN_VIEW = "WOTSTAT_CEF_MAIN_VIEW"


def copyFile(source, target):
  targetDir = os.path.dirname(target)
  if not os.path.exists(targetDir):
    os.makedirs(targetDir)
  data = ResMgr.openSection(source).asBinary
  if data:
    with open(target, "wb") as targetFile:
      targetFile.write(data)

def copyDir(source, target):
  for file in ResMgr.readDirectory(source):
    sourcePath = os.path.join(source, file)
    targetPath = os.path.join(target, file)
    if ResMgr.isDir(file):
      copyDir(sourcePath, targetPath)
    else:
      copyFile(sourcePath, targetPath)


# from subprocess import Popen, PIPE

# process = Popen(
#     ["C:/Users/Andrei/Desktop/cefapp/cefapp.exe"],
#     stdout=PIPE,
#     stderr=PIPE,
# )


# stdout, stderr = process.communicate()


def onAppInitialized(event):
  if event.ns == APP_NAME_SPACE.SF_LOBBY:
    app = ServicesLocator.appLoader.getApp(event.ns)  # type: AppEntry
    if not app:
      return

    uiLoader = dependency.instance(IGuiLoader)  # type: IGuiLoader
    parent = (
      uiLoader.windowsManager.getMainWindow()
      if uiLoader and uiLoader.windowsManager
      else None
    )

    app.loadView(SFViewLoadParams(CEF_MAIN_VIEW, parent=parent))


mainViewSettings = ViewSettings(
  CEF_MAIN_VIEW,
  MainView,
  "wotstat.cef.swf",
  WindowLayer.WINDOW,
  None,
  ScopeTemplates.GLOBAL_SCOPE,
)
g_entitiesFactories.addSettings(mainViewSettings)

g_eventBus.addListener(events.AppLifeCycleEvent.INITIALIZED, onAppInitialized, EVENT_BUS_SCOPE.GLOBAL)

copyDir('scripts/client/gui/mods/cefapp', 'mods/cefapp')