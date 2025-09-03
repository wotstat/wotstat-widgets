from constants import PREBATTLE_TYPE_NAMES, QUEUE_TYPE_NAMES, ROLE_TYPE_TO_LABEL
from post_progression_common import ACTION_TYPES
from helpers import dependency
from ..DataProviderSDK import DataProviderSDK
from PlayerEvents import g_playerEvents
from skeletons.gui.shared.utils import IHangarSpace
from CurrentVehicle import g_currentVehicle
from shared_utils import first
from items import vehicles
from gui.prb_control.dispatcher import _PreBattleDispatcher, g_prbLoader
from Event import Event
from . import logger

from ..hook import registerEvent
from ..ExceptionHandling import withExceptionHandling


class HangarProvider(object):
  
  hangarsSpace = dependency.descriptor(IHangarSpace) # type: IHangarSpace
  
  def __init__(self, sdk):
    # type: (DataProviderSDK) -> None
    
    self.isInHangar = sdk.createState(['hangar', 'isInHangar'], False)
    self.vehicle = sdk.createState(['hangar', 'vehicle', 'info'])
    self.crew = sdk.createState(['hangar', 'vehicle', 'crew'])
    self.optDevices = sdk.createState(['hangar', 'vehicle', 'optDevices'])
    self.shells = sdk.createState(['hangar', 'vehicle', 'shells'])
    self.consumables = sdk.createState(['hangar', 'vehicle', 'consumables'])
    self.boosters = sdk.createState(['hangar', 'vehicle', 'boosters'])
    self.isInBattle = sdk.createState(['hangar', 'vehicle', 'isInBattle'], False)
    self.isBroken = sdk.createState(['hangar', 'vehicle', 'isBroken'], False)
    self.postProgression = sdk.createState(['hangar', 'vehicle', 'postProgression'])
    self.xp = sdk.createState(['hangar', 'vehicle', 'xp'])
    self.battleMode = sdk.createState(['hangar', 'battleMode'])
    self.isInQueue = sdk.createState(['hangar', 'isInQueue'], False)
    self.onEnqueueTrigger = sdk.createTrigger(['hangar', 'onEnqueue'])
    self.onDequeueTrigger = sdk.createTrigger(['hangar', 'onDequeue'])
    
    g_playerEvents.onAccountBecomePlayer += self.__onAccountBecomePlayer
    g_playerEvents.onAccountBecomeNonPlayer += self.__onAccountBecomeNonPlayer
    
    global onBattleModeChange
    onBattleModeChange += self.__onBattleModeChange
    
    global onEnqueue
    onEnqueue += self.__onEnqueue
    
    g_playerEvents.onDequeued += self.__onDequeue
    
  @withExceptionHandling(logger)
  def __onAccountBecomePlayer(self):
    g_currentVehicle.onChanged += self.__onCurrentVehicleChanged
    self.__onCurrentVehicleChanged()
    self.isInHangar.setValue(True)
    
  @withExceptionHandling(logger)
  def __onAccountBecomeNonPlayer(self):
    g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged
    self.isInQueue.setValue(False)
    self.isInHangar.setValue(False)
  
  @withExceptionHandling(logger)
  def __onCurrentVehicleChanged(self, *args, **kwargs):
    item = g_currentVehicle.item
    
    if not item:
      return
    
    self.isBroken.setValue(item.isBroken)
    self.isInBattle.setValue(item.isInBattle)
    
    self.vehicle.setValue({
      'tag': item.typeDescr.name,
      'class': item.typeDescr.classTag,
      'role': ROLE_TYPE_TO_LABEL.get(item.typeDescr.role, 'None'),
      'level': item.typeDescr.level,
      'localizedName': item.typeDescr.userString,
      'localizedShortName': item.typeDescr.shortUserString,
    })
    
    self.crew.setValue([{
        'isFemale': t[1].isFemale,
        'efficiencyRoleLevel': t[1].efficiencyRoleLevel,
        'vehicleTag': t[1].getVehicle().name,
        'roles': t[1].roles(),
        'skills': [{
          'tag': s.name,
          'level': s.level,
        } for s in t[1].skills]
      } if t[1] else None for t in item.crew
    ])
    
    slots = [first(t.categories) for t in item.optDevices.slots]
    if item.optDevices.dynSlotTypeIdx < len(item.optDevices.slots) and item.optDevices.dynSlotType:
      slots[item.optDevices.dynSlotTypeIdx] = first(item.optDevices.dynSlotType.categories)
      
    installed = [vehicles.getItemByCompactDescr(t).name if t else None for t in item.optDevices.installed.getStorage]
    
    self.optDevices.setValue([{
        'tag': installed[i] if i < len(installed) else None,
        'specialization': slots[i],
      } for i in range(len(slots))
    ])
    
    self.shells.setValue([{
        'tag': t.type,
        'count': t.count,
      } for t in item.shells.installed.getItems()
    ])
    
    self.consumables.setValue([vehicles.getItemByCompactDescr(t).name if t else None for t in item.consumables.installed.getStorage])
    self.boosters.setValue([vehicles.getItemByCompactDescr(t).name if t else None for t in item.battleBoosters.installed.getStorage])
    
    postProgressionState = item.postProgression.getState()
    
    levels = filter(lambda t: t <= 10, postProgressionState.unlocks)
    level = max(levels) if len(levels) else 0
    features = {
      'optSwitchEnabled': 1 not in postProgressionState.disabledSwitches,
      'shellsSwitchEnabled': 2 not in postProgressionState.disabledSwitches,
    }
  
    currentSteps = [t for t in item.postProgression.iterOrderedSteps() if t.action.actionType == ACTION_TYPES.PAIR_MODIFICATION]
    modificationsName = [[m.getTechName() for m in t.action.modifications] for t in currentSteps]
    purchased = [t.action.getPurchasedModification() for t in currentSteps]
    unlockedModificationsName = [None if t.isLocked() else t.action.getTechName() for t in currentSteps]
    selectedModificationsName = [t.getTechName() if t else None for t in purchased]
    
    self.postProgression.setValue({
      'level': level,
      'features': features,
      'unlockedModifications': unlockedModificationsName,
      'selectedModifications': selectedModificationsName,
      'modifications': modificationsName,
    })
    
    self.xp.setValue(item.xp)
  
  @withExceptionHandling(logger)
  def __onBattleModeChange(self):
    dispatcher = g_prbLoader.getDispatcher()
    solo = QUEUE_TYPE_NAMES.get(dispatcher.getFunctionalState().entityTypeID, None)
    squad = PREBATTLE_TYPE_NAMES.get(dispatcher.getFunctionalState().entityTypeID, None)
    
    self.battleMode.setValue(squad if dispatcher.getFunctionalState().isInUnit() else solo)
    
  @withExceptionHandling(logger)
  def __onEnqueue(self, *a, **k):
    self.isInQueue.setValue(True)
    self.onEnqueueTrigger.trigger()
  
  @withExceptionHandling(logger)
  def __onDequeue(self, *a, **k):
    self.isInQueue.setValue(False)
    self.onDequeueTrigger.trigger()

onBattleModeChange = Event()
onEnqueue = Event()

@registerEvent(_PreBattleDispatcher, '_PreBattleDispatcher__setEntity')
def setEntity(self, *a, **k):
  onBattleModeChange()

try:
  from gui.Scaleform.daapi.view.lobby.battle_queue import BattleQueue
  @registerEvent(BattleQueue, '_populate')
  def queuePopulate(self, *a, **k): onEnqueue()
except Exception:
  from gui.Scaleform.daapi.view.lobby.battle_queue.battle_queue import BattleQueue
  @registerEvent(BattleQueue, '_populate')
  def queuePopulate(self, *a, **k): onEnqueue()