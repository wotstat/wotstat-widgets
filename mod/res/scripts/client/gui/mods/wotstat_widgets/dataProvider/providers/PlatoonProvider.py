import BigWorld
from constants import ROLE_TYPE_TO_LABEL
from ..DataProviderSDK import DataProviderSDK
from PlayerEvents import g_playerEvents
from helpers import dependency
from skeletons.gui.game_control import IPlatoonController
from items import vehicles as vehiclesUtils

from ..ExceptionHandling import withExceptionHandling

from . import logger

class PlatoonProvider(object):
  
  platoon = dependency.descriptor(IPlatoonController) # type: IPlatoonController

  def __init__(self, sdk):
    # type: (DataProviderSDK) -> None

    self.isInPlatoon = sdk.createState(['platoon', 'isInPlatoon'], False)
    self.maxSlots = sdk.createState(['platoon', 'maxSlots'], 0)
    self.commander = sdk.createState(['platoon', 'commander'])
    self.slots = sdk.createState(['platoon', 'slots'], [])
    
    self.platoon.onPlatoonTankVisualizationChanged += self.__onPlatoonUpdated
    self.platoon.onPlatoonTankUpdated += self.__onPlatoonUpdated
    self.platoon.onPlatoonTankRemove += self.__onPlatoonUpdated
    g_playerEvents.onAccountBecomePlayer += self.__onPlatoonUpdated
    
  @withExceptionHandling(logger)
  def __onPlatoonUpdated(self, *args, **kwargs):
    BigWorld.callback(0, self.__updateStats)

  @withExceptionHandling(logger)  
  def __updateStats(self):
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
        'rating': int(player.get('accountWTR').replace(',', '')),
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
    
    
    
  