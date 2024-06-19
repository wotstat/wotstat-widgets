import BigWorld


from .common.ServerLoggerBackend import ServerLoggerBackend
from .common.Logger import Logger, SimpleLoggerBackend
from .common.Config import Config
from .common.utils import copyDir
from .main.MainView import setup as mainViewSetup



DEBUG_MODE = '{{DEBUG_MODE}}'
CONFIG_PATH = './mods/configs/wotstat.cef/config.cfg'

logger = Logger.instance()

def copyCef():
  copyDir('scripts/client/gui/mods/cefapp', 'mods/cefapp')


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
    mainViewSetup()

    logger.info("WotStatWidget started")

