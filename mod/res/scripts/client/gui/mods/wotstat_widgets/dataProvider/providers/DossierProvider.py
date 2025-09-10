from Avatar import PlayerAvatar
import BigWorld
from Event import Event
from Vehicle import Vehicle
from CurrentVehicle import g_currentVehicle
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK
from skeletons.gui.shared import IItemsCache
from helpers import dependency

from PlayerEvents import g_playerEvents
from items import vehicles
from gui.shared.gui_items.dossier import VehicleDossier
from gui.shared.gui_items.dossier.achievements.mark_on_gun import MarkOnGunAchievement

from ..DataProviderSDK import DataProviderSDK
from ..hook import registerEvent
from ..ExceptionHandling import withExceptionHandling
from . import logger

def playerDbId():
  player = BigWorld.player()
  
  if hasattr(player, 'databaseID'):
    return player.databaseID
  
  if hasattr(player, 'arena'):
    vehicle = player.arena.vehicles.get(player.playerVehicleID, None)
    if vehicle: return vehicle.get('accountDBID', 0)
    
  return 0
    

class DossierCache(object):
  def __init__(self):
    self.cache = {}
  
  def get(self, vehicleIntCd):
    playerId = playerDbId()
    player = self.cache.get(playerId)
    if not player:
      return None
    return player.get(vehicleIntCd, None)
  
  def set(self, vehicleIntCd, value):
    playerId = playerDbId()
    player = self.cache.get(playerId)
    if not player:
      player = {}
      self.cache[playerId] = player
    player[vehicleIntCd] = value

class DossierProvider(object):
  itemsCache = dependency.descriptor(IItemsCache) # type: IItemsCache
  
  def __init__(self, sdk):
    # type: (DataProviderSDK) -> None
    
    self.dossierCache = DossierCache()
    
    self.current = sdk.createState(['dossier', 'current'])
    
    g_playerEvents.onAccountBecomePlayer += self.__onAccountBecomePlayer
    g_playerEvents.onAccountBecomeNonPlayer += self.__onAccountBecomeNonPlayer
    
    global onVehicleChanged, onMarkOnGunAchievementInit
    onMarkOnGunAchievementInit += self.__onMarkOnGunAchievementInit
    onVehicleChanged += self.__onVehicleChanged
    
  @withExceptionHandling(logger)
  def __onVehicleChanged(self, *a, **k):
    self.__updateDossierOnVehicleChanged()
    
  @withExceptionHandling(logger)
  def __onAccountBecomePlayer(self):
    g_currentVehicle.onChanged += self.__updateDossierOnVehicleChanged
    
  @withExceptionHandling(logger)
  def __onAccountBecomeNonPlayer(self):
    g_currentVehicle.onChanged -= self.__updateDossierOnVehicleChanged
    
  def __onMarkOnGunAchievementInit(self, obj, dossier, *a, **k):
    # type: (MarkOnGunAchievement, VehicleDossier) -> None
    self.dossierCache.set(dossier.getCompactDescriptor(), self.__dossierToDict(dossier))
    
  def __updateDossierOnVehicleChanged(self, *a, **k):
    if g_currentVehicle and g_currentVehicle.item:
      cd = g_currentVehicle.item.intCD
      dossier = self.itemsCache.items.getVehicleDossier(cd)
      if dossier:
        target = self.__dossierToDict(dossier)
        self.dossierCache.set(cd, target)
        self.current.setValue(target)
      else:
        self.current.setValue(None)
        
    else:
      if not BigWorld.player() or not hasattr(BigWorld.player(), 'playerVehicleID'): return
      vehicle = BigWorld.entity(BigWorld.player().playerVehicleID) # type: Vehicle
      if not vehicle: return
      intCd = vehicle.typeDescriptor.type.compactDescr
      target = self.dossierCache.get(intCd)
      self.current.setValue(target)
  
  @withExceptionHandling(logger)
  def __dossierToDict(self, dossier):
    # type: (VehicleDossier) -> None
    return {
      'vehicleTag': vehicles.getItemByCompactDescr(dossier.getCompactDescriptor()).name,
      'movingAvgDamage': dossier.getRecordValue(ACHIEVEMENT_BLOCK.TOTAL, 'movingAvgDamage'),
      'damageRating': dossier.getRecordValue(ACHIEVEMENT_BLOCK.TOTAL, 'damageRating') / 100.0,
      'battlesCount': dossier.getRandomStats().getBattlesCount(),
    }


onVehicleChanged = Event()
onMarkOnGunAchievementInit = Event()

@registerEvent(PlayerAvatar, 'onVehicleChanged')
def playerAvatarOnVehicleChanged(self, *a, **k):
  onVehicleChanged(self, *a, **k)
  
@registerEvent(MarkOnGunAchievement, '__init__')
def markOnGunAchievementInit(self, dossier, *a, **k):
  onMarkOnGunAchievementInit(self, dossier, *a, **k)