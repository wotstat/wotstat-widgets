from BattleFeedbackCommon import BATTLE_EVENT_TYPE
from gui.battle_control.arena_info.arena_vos import VehicleArenaInfoVO
from gui.battle_control.controllers.vehicle_state_ctrl import VehicleStateController
from ..DataProviderSDK import DataProviderSDK
from items import vehicles as itemsVehicles
from constants import ROLE_TYPE_TO_LABEL, ATTACK_REASONS, BATTLE_LOG_SHELL_TYPES
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider, IArenaDataProvider
from gui.battle_control.controllers.feedback_events import _CritsExtra, _DamageExtra, _MultiStunExtra, _VisibilityExtra, PlayerFeedbackEvent
from typing import List
from ..crossGameUtils import getBattleLogShellTypesNames

from ..ExceptionHandling import logCurrentException, withExceptionHandling
from . import logger

IGNORE = 'IGNORE'

BATTLE_LOG_SHELL_TYPES_NAMES = getBattleLogShellTypesNames()
ATTACK_REASONS_MAX = len(ATTACK_REASONS)

class PlayerFeedbackProvider(object):
  sessionProvider = dependency.descriptor(IBattleSessionProvider) # type: IBattleSessionProvider

  def __init__(self, sdk):
    # type: (DataProviderSDK) -> None
    
    self.onPlayerFeedback = sdk.createTrigger(['battle', 'onPlayerFeedback'])
    
    self.sessionProvider.onBattleSessionStart += self.__onBattleSessionStart
    self.sessionProvider.onBattleSessionStop += self.__onBattleSessionStop
    
    self.battleEventProcessors = {
      BATTLE_EVENT_TYPE.SPOTTED:                self.processAnyVisibilityExtra('spotted'),
      BATTLE_EVENT_TYPE.TARGET_VISIBILITY:      self.processAnyVisibilityExtra('targetVisibility'),
      BATTLE_EVENT_TYPE.DETECTED:               self.processAnyVisibilityExtra('detected'),
      BATTLE_EVENT_TYPE.RADIO_ASSIST:           self.processAnyDamageExtra('radioAssist'),
      BATTLE_EVENT_TYPE.TRACK_ASSIST:           self.processAnyDamageExtra('trackAssist'),
      BATTLE_EVENT_TYPE.TANKING:                self.processAnyDamageExtra('tanking'),
      BATTLE_EVENT_TYPE.DAMAGE:                 self.processAnyDamageExtra('damage'),
      BATTLE_EVENT_TYPE.SMOKE_ASSIST:           self.processAnyDamageExtra('smokeAssist'),
      BATTLE_EVENT_TYPE.INSPIRE_ASSIST:         self.processAnyDamageExtra('inspireAssist'),
      BATTLE_EVENT_TYPE.RECEIVED_DAMAGE:        self.processAnyDamageExtra('receivedDamage'),
      BATTLE_EVENT_TYPE.STUN_ASSIST:            self.processAnyDamageExtra('stunAssist'),
      BATTLE_EVENT_TYPE.CRIT:                   self.processAnyCritsExtra('crit'),
      BATTLE_EVENT_TYPE.RECEIVED_CRIT:          self.processAnyCritsExtra('receivedCrit'),
      BATTLE_EVENT_TYPE.ENEMY_SECTOR_CAPTURED:  self.processNamedEvent('enemySectorCaptured'),
      BATTLE_EVENT_TYPE.DESTRUCTIBLE_DESTROYED: self.processNamedEvent('destructibleDestroyed'),
      BATTLE_EVENT_TYPE.DEFENDER_BONUS:         self.processNamedEvent('defenderBonus'),
      BATTLE_EVENT_TYPE.KILL:                   self.processAnyVehicleEvent('kill'),
      BATTLE_EVENT_TYPE.BASE_CAPTURE_DROPPED:   self.processExtraAsValue('baseCaptureDropped', 'points'),
      BATTLE_EVENT_TYPE.DESTRUCTIBLE_DAMAGED:   self.processExtraAsValue('destructibleDamaged', 'damage'),
      BATTLE_EVENT_TYPE.DESTRUCTIBLES_DEFENDED: self.processExtraAsValue('destructiblesDefended', 'extra'),
      BATTLE_EVENT_TYPE.BASE_CAPTURE_POINTS:    self.processBaseCapturePoints,
      BATTLE_EVENT_TYPE.BASE_CAPTURE_BLOCKED:   self.processBaseCaptureBlocked,
      BATTLE_EVENT_TYPE.MULTI_STUN:             self.processMultiStun,
      BATTLE_EVENT_TYPE.EQUIPMENT_TIMER_EXPIRED: None,
    }
    
    # WG
    try: self.battleEventProcessors[BATTLE_EVENT_TYPE.VEHICLE_HEALTH_ADDED] = self.processExtraAsValue('vehicleHealthAdded', 'health')
    except: pass
    
  @withExceptionHandling(logger)
  def __onBattleSessionStart(self):
    self.sessionProvider.shared.feedback.onPlayerFeedbackReceived += self.__onPlayerFeedbackReceived
    self.sessionProvider.shared.feedback.onVehicleDetected += self.__onVehicleDetected
    self.arenaDataProvider = self.sessionProvider.getArenaDP() # type: IArenaDataProvider
    self.vehicleState = self.sessionProvider.shared.vehicleState # type: VehicleStateController
    
  @withExceptionHandling(logger)
  def __onBattleSessionStop(self):
    if not self.sessionProvider.shared.feedback: return
    self.sessionProvider.shared.feedback.onPlayerFeedbackReceived -= self.__onPlayerFeedbackReceived
    self.sessionProvider.shared.feedback.onVehicleDetected -= self.__onVehicleDetected

  @withExceptionHandling(logger)
  def __onPlayerFeedbackReceived(self, events):
    # type: (List[PlayerFeedbackEvent]) -> None
    for event in events:
      self.processEvent(event)
      
  @withExceptionHandling(logger)
  def __onVehicleDetected(self, feedback):
    # type: (PlayerFeedbackEvent) -> None
    self.processEvent(feedback)
  
  def processEvent(self, event):
    # type: (PlayerFeedbackEvent) -> any
    
    if self.vehicleState.getControllingVehicleID() != self.arenaDataProvider.getPlayerVehicleID():
      return
    
    eventType = event.getBattleEventType()
    if eventType not in self.battleEventProcessors:
      logger.error('Unknown battle event type: %s' % str(eventType))
      
      try:
        processed = self.processByExtraType(event)
        if processed == IGNORE: return
        self.onPlayerFeedback.trigger({ 'type': str(eventType), 'data': processed[1] if len(processed) > 1 else None })
      except Exception as e:
        logCurrentException('Error processing battle event', logger)
        self.onPlayerFeedback.trigger({ 'type': str(eventType), 'data': None })
      
      return
    
    if self.battleEventProcessors[eventType] is None:
      return
    
    try:
      processed = self.battleEventProcessors[eventType](event)
      if processed == IGNORE: return
    except Exception as e:
      logCurrentException('Error processing battle event', logger)
      return
    
    eventName = processed[0]
    data = processed[1] if len(processed) > 1 else None
    self.onPlayerFeedback.trigger({ 'type': eventName, 'data': data })
  
  # Shared event processors
  def vehicleById(self, vehicleID):
    targetVehicle = self.arenaDataProvider.getVehicleInfo(vehicleID) # type: VehicleArenaInfoVO
    if targetVehicle is None: return None
    
    typeInfo = targetVehicle.vehicleType
    
    if typeInfo.compactDescr == 0: return IGNORE
    
    return {
      'tag': itemsVehicles.getItemByCompactDescr(typeInfo.compactDescr).name if typeInfo.compactDescr > 0 else None,
      'localizedName': typeInfo.shortName,
      'localizedShortName': typeInfo.name,
      'level': typeInfo.level,
      'class': typeInfo.classTag,
      'role': ROLE_TYPE_TO_LABEL.get(typeInfo.role, 'None'),
      'team': targetVehicle.team,
      'playerName': targetVehicle.player.name if targetVehicle.player else None,
      'playerId': targetVehicle.player.accountDBID if targetVehicle.player else None,
    }
  
  def processByExtraType(self, event):
    # type: (PlayerFeedbackEvent) -> any
    extra = event.getExtra()
    
    if isinstance(extra, _DamageExtra):
      return self.processAnyDamageExtra('damage')(extra)
    elif isinstance(extra, _CritsExtra):
      return self.processAnyCritsExtra('crit')(extra)
    elif isinstance(extra, _VisibilityExtra):
      return self.processAnyVisibilityExtra('visibility')(extra)
    elif isinstance(extra, _MultiStunExtra):
      return self.processMultiStun(extra)
    elif isinstance(extra, int):
      return ('value', { 'value': extra })
    else:
      return ('extra', { 'extra': extra })
  
  def processAnyVisibilityExtra(self, name):
    # type: (str) -> any
    
    def wrapper(event):
      # type: (PlayerFeedbackEvent) -> any
      extra = event.getExtra() # type: _VisibilityExtra
      veh = self.vehicleById(event.getTargetID())
      if veh == IGNORE: return IGNORE
      
      return (name, {
        'isVisible': bool(extra.isVisible()),
        'isDirect': bool(extra.isDirect()),
        'isRoleAction': bool(extra.isRoleAction()),
        'vehicle': veh
      })
    
    return wrapper
  
  def processAnyDamageExtra(self, name):
    # type: (str) -> any
    
    def wrapper(event):
      # type: (PlayerFeedbackEvent) -> any
      extra = event.getExtra() # type: _DamageExtra
      veh = self.vehicleById(event.getTargetID())
      
      reason = ATTACK_REASONS[extra.getAttackReasonID()] if extra.getAttackReasonID() < ATTACK_REASONS_MAX else None
      secondaryReason = ATTACK_REASONS[extra.getSecondaryAttackReasonID()] if extra.getSecondaryAttackReasonID() < ATTACK_REASONS_MAX else None
      shellType = extra.getShellType()
      
      return (name, {
        'damage': extra.getDamage(),
        'attackReason': reason,
        'secondaryReason': secondaryReason,
        'shellType': BATTLE_LOG_SHELL_TYPES_NAMES.get(shellType, int(shellType) if shellType else None),
        'vehicle': veh
      })
    
    return wrapper

  def processAnyCritsExtra(self, name):
    # type: (str) -> any
    
    def wrapper(event):
      # type: (PlayerFeedbackEvent) -> any
      extra = event.getExtra() # type: _CritsExtra
      veh = self.vehicleById(event.getTargetID())
      
      reasonId = extra._CritsExtra__attackReasonID
      secondaryReasonId = extra._CritsExtra__secondaryAttackReasonID
      reason = ATTACK_REASONS[reasonId] if reasonId < ATTACK_REASONS_MAX else None
      secondaryReason = ATTACK_REASONS[secondaryReasonId] if secondaryReasonId < ATTACK_REASONS_MAX else None
      shellType = extra.getShellType()
        
      return (name, {
        'critsCount': extra.getCritsCount(),
        'attackReason': reason,
        'secondaryReason': secondaryReason,
        'shellType': BATTLE_LOG_SHELL_TYPES_NAMES.get(shellType, int(shellType) if shellType else None),
        'vehicle': veh
      })
    
    return wrapper
  
  def processAnyVehicleEvent(self, name):
    # type: (str) -> any
    
    def wrapper(event):
      # type: (PlayerFeedbackEvent) -> any
      veh = self.vehicleById(event.getTargetID())
      return (name, { 'vehicle': veh })
    
    return wrapper

  def processNamedEvent(self, name):
    # type: (str) -> any
    
    def wrapper(event):
      # type: (PlayerFeedbackEvent) -> any
      return (name,)
    
    return wrapper

  def processExtraAsValue(self, name, extraValueName):
    # type: (str, str) -> any
    
    def wrapper(event):
      # type: (PlayerFeedbackEvent) -> any
      return (name, { extraValueName: event.getExtra() })
    
    return wrapper  

  # Specific event processors
  def processMultiStun(self, event):
    # type: (PlayerFeedbackEvent) -> any
    extra = event.getExtra() # type: _MultiStunExtra
    logger.info('Multi stun event: %s' % event.getTargetID())
    return ('multiStun', { 'stunCount': extra.getTargetsAmount() })

  def processBaseCapturePoints(self, event):
    # type: (PlayerFeedbackEvent) -> any
    return ('baseCapturePoints', { 'points': event.getExtra(), 'session': event.getTargetID() })
  
  def processBaseCaptureBlocked(self, event):
    # type: (PlayerFeedbackEvent) -> any
    return ('baseCaptureBlocked', { 'points': event.getExtra(), 'session': event.getTargetID() })
