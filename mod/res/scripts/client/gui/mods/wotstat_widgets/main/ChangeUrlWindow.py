import BigWorld
from frameworks.wulf.gui_constants import WindowLayer
from gui.Scaleform.framework import g_entitiesFactories, ScopeTemplates, ViewSettings
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from gui.Scaleform.framework.application import AppEntry
from gui.shared.formatters import text_styles

from ..common.i18n import t
from ..common.Logger import Logger

from .EventsManager import manager

CEF_CHANGE_URL_WINDOW = "WOTSTAT_CEF_CHANGE_URL_WINDOW"

logger = Logger.instance()

class ChangeUrlWindow(AbstractWindowView):
  
  def __init__(self, ctx=None):
    super(ChangeUrlWindow, self).__init__(ctx)
    self.ctx = ctx
    
  def onWindowClose(self):
    self.destroy()
  
  def py_changeUrl(self, url):
    logger.info('ChangeUrlWindow.py: py_changeUrl: url: %s' % url)
    wid = self.ctx.get('wid', None)
    if wid is not None:
      manager.changeUrl(wid, url)
    self.destroy()
    
  def py_cancel(self):
    self.destroy()

  def py_t(self, key):
    return t(key)
  
  def _populate(self):
    super(ChangeUrlWindow, self)._populate()
    self._as_setUrl(self.ctx.get('url', ''))

  def _dispose(self):
    super(ChangeUrlWindow, self)._dispose()
    
  def _as_setUrl(self, url):
    self.flashObject.as_setUrl(url)

def setup():
  settingsViewSettings = ViewSettings(
    CEF_CHANGE_URL_WINDOW,
    ChangeUrlWindow,
    "wotstat.widgets.changeUrlWindow.swf",
    WindowLayer.TOP_WINDOW,
    None,
    ScopeTemplates.VIEW_SCOPE,
  )
  g_entitiesFactories.addSettings(settingsViewSettings)
  

def show(wid, url):
  appLoader = dependency.instance(IAppLoader) # type: IAppLoader
  app = appLoader.getApp() # type: AppEntry
  app.loadView(SFViewLoadParams(CEF_CHANGE_URL_WINDOW), ctx={'url': url, 'wid': wid})