import os
import zipfile

import BigWorld

from .common.ServerLoggerBackend import ServerLoggerBackend
from .common.Logger import Logger, SimpleLoggerBackend
from .common.Config import Config
from .common.utils import copyFile
from .main.MainView import setup as mainViewSetup
from .main.CefServer import server

from .constants import CEF_PATH, CONFIG_PATH

DEBUG_MODE = '{{DEBUG_MODE}}'

logger = Logger.instance()

def copyCef():
  logger.info("Copy CEF to %s" % CEF_PATH)
  copyFile('wotstat.widget.cef.zip', 'mods/wotstat.widget.cef.zip')
  zipfile.ZipFile('mods/wotstat.widget.cef.zip').extractall('mods')
  os.remove('mods/wotstat.widget.cef.zip')


class WotstatWidget(object):
  def __init__(self):
    logger.info("Starting WotStatWidget")

    self.config = Config(CONFIG_PATH)

    version = self.config.get("version")
    logger.info("Config loaded. Version: %s" % version)

    logger.setup([
      SimpleLoggerBackend(prefix="[MOD_WOTSTAT_WIDGET]", minLevel="INFO" if not DEBUG_MODE else "DEBUG"),
      ServerLoggerBackend(url=self.config.get('lokiURL'),
                          prefix="[MOD_WOTSTAT_WIDGET]",
                          source="mod_widget",
                          modVersion=version,
                          minLevel="INFO")
    ])

    copyCef()
    server.enable(self.config.get('devtools'))
    mainViewSetup()

    logger.info("WotStatWidget started")


  def fini(self):
    logger.info("Stopping WotStatWidget")
    server.dispose()

