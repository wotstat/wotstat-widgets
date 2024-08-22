import base64
from Avatar import PlayerAvatar
import BattleReplay
import BigWorld
from Event import Event

from PlayerEvents import g_playerEvents
from ..hook import registerEvent
from ..thirdParty.FixedBattleResultsCache import setup
from ..DataProviderSDK import DataProviderSDK
from ..ExceptionHandling import withExceptionHandling

from . import logger

def prepareString(obj):
  if isinstance(obj, str):
    try:
      obj.decode('utf-8')
    except UnicodeDecodeError:
      return base64.b64encode(obj)
  return obj

def preprocessData(obj):
  if isinstance(obj, set):
    return list(obj)
  elif isinstance(obj, str):
    return prepareString(obj)
  elif isinstance(obj, dict):
    return { prepareString(str(k)): preprocessData(v) for k, v in obj.items() }
  elif isinstance(obj, list):
    return [preprocessData(i) for i in obj]
  elif isinstance(obj, tuple):
    return [preprocessData(i) for i in obj]
  return obj

class BattleResultProvider(object):
  
  def __init__(self, sdk):
    # type: (DataProviderSDK) -> None
    
    self.onBattleResult = sdk.createTrigger(['battle', 'onBattleResult'])
    logger.info(setup())
    
    self.arenaUniqueIdQueue = []
    
    global onEnterWorld
    onEnterWorld += self.__onEnterWorld
    
    g_playerEvents.onBattleResultsReceived += self.__onBattleResultsReceived
    
    self.battleResultsCacheLoop()
    
  @withExceptionHandling(logger)
  def __onBattleResultsReceived(self, isPlayerVehicle, results):
    if not isPlayerVehicle or BattleReplay.isPlaying(): return
    self.processResult(results)
    
  @withExceptionHandling(logger)
  def __onEnterWorld(self, *args, **kwargs):
    # type: (*any, **any) -> None
    self.arenaUniqueIdQueue.append(BigWorld.player().arenaUniqueID)
        
  def battleResultsCacheLoop(self):
    BigWorld.callback(1, self.battleResultsCacheLoop)
    
    def resultCallback(code, result):
      if code > 0:
        self.processResult(result)

    if len(self.arenaUniqueIdQueue) > 0:
      arenaID = self.arenaUniqueIdQueue.pop(0)
      self.arenaUniqueIdQueue.append(arenaID)
      try:
        BigWorld.player().battleResultsCache.get(arenaID, resultCallback)
      except:
        pass
    
  def processResult(self, results):
    # type: (dict) -> None
    arenaUniqueID = results.get('arenaUniqueID')
    
    if arenaUniqueID not in self.arenaUniqueIdQueue:
      logger.info('BattleResultProvider: Received battle result for unknown arenaUniqueID: %s' % arenaUniqueID)
      return
    
    while arenaUniqueID in self.arenaUniqueIdQueue:
      self.arenaUniqueIdQueue.remove(arenaUniqueID)
    
    logger.info('BattleResultProvider: Processing battle result for arenaUniqueID: %s' % arenaUniqueID)
    self.onBattleResult.trigger(preprocessData(results))
  
    
onEnterWorld = Event()
@registerEvent(PlayerAvatar, 'onEnterWorld')
def enterWorld(self, *a, **k):
  onEnterWorld(self, *a, **k)
