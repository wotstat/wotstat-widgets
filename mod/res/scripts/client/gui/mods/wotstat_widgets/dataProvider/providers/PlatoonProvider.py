import BigWorld
import re

from constants import ROLE_TYPE_TO_LABEL
from ..DataProviderSDK import DataProviderSDK
from PlayerEvents import g_playerEvents
from helpers import dependency
from skeletons.gui.game_control import IPlatoonController
from items import vehicles as vehiclesUtils
from skeletons.gui.shared.utils import IHangarSpace

from ..ExceptionHandling import withExceptionHandling

from . import logger

def formattedToInt(numberStr):
  cleanedStr = re.sub(r'[^\d]', '', numberStr)
  try: return int(cleanedStr)
  except: return 0

# TODO:
# def _DynSquadFunctional_updateVehiclesInfo(self, updated, arenaDP):
#         # is dynamic squad created
#   if avatar_getter.getArena().guiType == constants.ARENA_GUI_TYPE.RANDOM:
#     for flags, vo in updated:
#       if flags & INVALIDATE_OP.PREBATTLE_CHANGED and vo.squadIndex > 0:
#         g_battle.updatePlayerState(vo.vehicleID, INV.SQUAD_INDEX) # | INV.PLAYER_STATUS

class PlatoonProvider(object):
  
  platoon = dependency.descriptor(IPlatoonController) # type: IPlatoonController
  hangarSpace = dependency.descriptor(IHangarSpace) # type: IHangarSpace

  def __init__(self, sdk):
    # type: (DataProviderSDK) -> None

    self.isInPlatoon = sdk.createState(['platoon', 'isInPlatoon'], False)
    self.maxSlots = sdk.createState(['platoon', 'maxSlots'], 0)
    self.commander = sdk.createState(['platoon', 'commander'])
    self.slots = sdk.createState(['platoon', 'slots'], [])
    self.enabled = True
    
    g_playerEvents.onAccountBecomePlayer += self.__onAccountBecomePlayer
    g_playerEvents.onAccountBecomeNonPlayer += self.__onAccountBecomeNonPlayer
    self.hangarSpace.onSpaceCreate += self.__onHangarSpaceCreate
    
    self.platoon.onMembersUpdate += self.__onPlatoonUpdated
    self.platoon.onPlatoonTankVisualizationChanged += self.__onPlatoonUpdated
    self.platoon.onPlatoonTankUpdated += self.__onPlatoonUpdated
    self.platoon.onPlatoonTankRemove += self.__onPlatoonUpdated
    
  @withExceptionHandling(logger)
  def __onPlatoonUpdated(self, *a, **k):
    BigWorld.callback(0, self.__updateStats)
    
  def __onAccountBecomeNonPlayer(self, *a, **k):
    self.enabled = False
    
  def __onAccountBecomePlayer(self, *a, **k):
    self.enabled = True
    
  def __onHangarSpaceCreate(self, *a, **k):
    BigWorld.callback(0, self.__updateStats)

  @withExceptionHandling(logger)  
  def __updateStats(self):
    if not self.enabled: return
    
    self.isInPlatoon.setValue(self.platoon.isInPlatoon())
    self.maxSlots.setValue(self.platoon.getMaxSlotCount())
    
    if not self.platoon.isInPlatoon():
      self.commander.setValue(None)
      self.slots.setValue([])
      return
    
    slots = self.platoon.getPlatoonSlotsData()
    
    for i in range(len(slots)):
      player = slots[i].get('player')
      if player and player.get('isCommander'):
        self.commander.setValue(i)
        break
      
    processed = []
    
    for slot in slots:
      player = slot.get('player')
      if player is None:
        processed.append(None)
        continue
      
      vehicleDescr = slot.get('selectedVehicle')
      vehicle = vehiclesUtils.getItemByCompactDescr(vehicleDescr.get('intCD')) if vehicleDescr else None
      processed.append({
        'name': player.get('userName'),
        'clanTag': player.get('clanAbbrev'),
        'dbid': player.get('dbID'),
        'rating': formattedToInt(player.get('accountWTR', '0')),
        'timeJoin': player.get('timeJoin'),
        'isOffline': player.get('isOffline'),
        'isReady': player.get('readyState'),
        'vehicle': {
          'tag': vehicle.name,
          'class': vehicle.classTag,
          'role': ROLE_TYPE_TO_LABEL.get(vehicle.role, 'None'),
          'level': vehicle.level,
          'localizedName': vehicle.userString,
          'localizedShortName': vehicle.shortUserString,  
        } if vehicle and player.get('readyState') else None
      })
    
    self.slots.setValue(processed)
    
    
    
  