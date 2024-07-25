from typing import List  # noqa: F401
from Singleton import Singleton

LEVELS_ORDER = {
  "DEBUG" : 0, 
  "INFO" : 1, 
  "WARN" : 2, 
  "ERROR" : 3, 
  "CRITICAL" : 4
}

def getLevelOrder(level):
  return LEVELS_ORDER[level] if level in LEVELS_ORDER else -1


class ILoggerBackend:
  def printLog(self, level, log):
    # type: (str, str) -> None
    pass

class SimpleLoggerBackend(ILoggerBackend):
  def __init__(self, prefix, minLevel="INFO"):
    self.prefix = prefix
    self.minLevelOrder = getLevelOrder(minLevel)

  def printLog(self, level, log):
    if getLevelOrder(level) >= self.minLevelOrder:
      print("%s[%s]: %s" % (self.prefix, level, str(log)))

class Logger(Singleton):

  @staticmethod
  def instance():
    return Logger()
  
  def _singleton_init(self):
    self.isSetup = False
    self.backends = [] # type: List[ILoggerBackend]
    self.preSetupQueue = []

  def setup(self, backends):
    # type: (List[ILoggerBackend]) -> None
    self.backends = backends
    self.isSetup = True

    for log in self.preSetupQueue:
      self.printLog(log[0], log[1])
    
    self.preSetupQueue = []

  def printLog(self, level, log):
    if not self.isSetup:
      self.preSetupQueue.append((level, log))
      return
    
    for backend in self.backends:
      backend.printLog(level, log)

  def debug(self, log):
    self.printLog("DEBUG", log)

  def info(self, log):
    self.printLog("INFO", log)

  def warn(self, log):
    self.printLog("WARN", log)

  def error(self, log):
    self.printLog("ERROR", log)

  def critical(self, log):
    self.printLog("CRITICAL", log)