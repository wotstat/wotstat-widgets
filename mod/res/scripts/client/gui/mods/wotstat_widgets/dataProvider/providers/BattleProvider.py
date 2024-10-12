import BigWorld
from ClientArena import ClientArena
import TriggersManager
from constants import ROLE_TYPE_TO_LABEL, ARENA_BONUS_TYPE_IDS, ARENA_GAMEPLAY_NAMES, ATTACK_REASONS, ARENA_PERIOD_NAMES
from helpers import dependency
from items.vehicles import VehicleDescriptor
from items import vehicles as itemsVehicles
from skeletons.gui.battle_session import IArenaDataProvider, IBattleSessionProvider
from gui.battle_control.arena_info.arena_vos import VehicleArenaInfoVO
from helpers.i18n import makeString
import copy

from vehicle_systems.vehicle_damage_state import VehicleDamageState

from ..DataProviderSDK import DataProviderSDK
from Avatar import PlayerAvatar
from Vehicle import Vehicle
from Event import Event
from gun_rotation_shared import decodeGunAngles

from ..hook import registerEvent
from ..ExceptionHandling import withExceptionHandling
from . import logger

class BattleProvider(TriggersManager.ITriggerListener):
  
  sessionProvider = dependency.descriptor(IBattleSessionProvider) # type: IBattleSessionProvider

  def __init__(self, sdk):
    # type: (DataProviderSDK) -> None
    
    self.started = False
    self.battleLoopCallbackHandler = None
    
    self.arena = sdk.createState(['battle', 'arena'], None)
    self.arenaId = sdk.createState(['battle', 'arenaId'], None)
    self.vehicle = sdk.createState(['battle', 'vehicle'], None)
  
    self.health = sdk.createState(['battle', 'health'], None)
    self.maxHealth = sdk.createState(['battle', 'maxHealth'], None)
    self.isAlive = sdk.createState(['battle', 'isAlive'], None)
    
    self.onDamageTrigger = sdk.createTrigger(['battle', 'onDamage'])
    self.isInBattle = sdk.createState(['battle', 'isInBattle'], False)
    self.arenaPeriod = sdk.createState(['battle', 'period'], None)
    self.teamBases = sdk.createState(['battle', 'teamBases'], None)
    self.position = sdk.createState(['battle', 'position'], None)
    self.rotation = sdk.createState(['battle', 'rotation'], None)
    self.speedInfo = sdk.createState(['battle', 'velocity'], (0.0, 0.0))
    self.turretYaw = sdk.createState(['battle', 'turretYaw'], 0.0)
    self.gunPitch = sdk.createState(['battle', 'gunPitch'], 0.0)
    self.turretRotationSpeed = sdk.createState(['battle', 'turretRotationSpeed'], 0.0)
    
    TriggersManager.g_manager.addListener(self)
    
    global onEnterWorld, onVehicleChanged, onHealthChanged, onVehicleDamageStateUpdate
    onEnterWorld += self.__onEnterWorld
    onVehicleChanged += self.__onVehicleChanged
    onHealthChanged += self.__onHealthChanged
    onVehicleDamageStateUpdate += self.__onVehicleDamageStateUpdate
    
    self.sessionProvider.onBattleSessionStart += self.__onBattleSessionStart
    self.sessionProvider.onBattleSessionStop += self.__onBattleSessionStop
    self.arenaDataProvider = self.sessionProvider.getArenaDP() # type: IArenaDataProvider
    
  @withExceptionHandling(logger)
  def __onBattleSessionStart(self):
    arena = BigWorld.player().arena # type: ClientArena
    arena.onVehicleUpdated += self.__onVehicleUpdated
    arena.onPeriodChange += self.__onArenaPeriodChange
    arena.onTeamBasePointsUpdate += self.__onTeamBasePointsUpdate
    
    self.arenaDataProvider = self.sessionProvider.getArenaDP() # type: IArenaDataProvider
    
    self.arenaPeriod.setValue({
      'tag': ARENA_PERIOD_NAMES[arena.period],
      'endTime': arena.periodEndTime,
      'length': arena.periodLength,
    })
    
    self.started = True
    self.__updateLoop()
  
  @withExceptionHandling(logger)
  def __onBattleSessionStop(self):
    if not BigWorld.player(): return
    arena = BigWorld.player().arena # type: ClientArena
    arena.onVehicleUpdated -= self.__onVehicleUpdated
    arena.onPeriodChange -= self.__onArenaPeriodChange
    arena.onTeamBasePointsUpdate -= self.__onTeamBasePointsUpdate
    self.arena.setValue(None)
    self.arenaId.setValue(None)
    self.vehicle.setValue(None)
    self.health.setValue(None)
    self.maxHealth.setValue(None)
    self.isAlive.setValue(None)
    self.arenaPeriod.setValue(None)
    self.teamBases.setValue(None)
    self.position.setValue(None)
    self.rotation.setValue(None)
    self.isInBattle.setValue(False)
    
    self.started = False
    if self.battleLoopCallbackHandler:
      BigWorld.cancelCallback(self.battleLoopCallbackHandler)
    self.battleLoopCallbackHandler = None
    
  @withExceptionHandling(logger)
  def __onEnterWorld(self, obj, *a, **k):
    player = BigWorld.player()
    arena = player.arena # type: ClientArena
    
    self.arenaId.setValue(player.arenaUniqueID)
    self.arena.setValue({
      'tag': arena.arenaType.geometryName,
      'localizedName': makeString('#arenas:%s/name' % arena.arenaType.geometryName),
      'mode': ARENA_BONUS_TYPE_IDS.get(player.arena.bonusType, None),
      'gameplay': ARENA_GAMEPLAY_NAMES[player.arenaTypeID >> 16],
      'team': player.team
    })
    
    self.isInBattle.setValue(True)
  
  @withExceptionHandling(logger)
  def __onVehicleUpdated(self, *a, **k):
    vid = BigWorld.player().playerVehicleID
    vehicle = BigWorld.entity(vid) # type: Vehicle
    if not vehicle:
      return
    self.health.setValue(vehicle.health)
    self.maxHealth.setValue(vehicle.maxHealth)
    self.isAlive.setValue(bool(vehicle.isAlive()))
    
  def typeDescriptorToVehicleInfo(self, typeDescriptor):
    # type: (VehicleDescriptor) -> dict
    return {
      'tag': typeDescriptor.name,
      'localizedName': typeDescriptor.type.userString,
      'localizedShortName': typeDescriptor.type.shortUserString,
      'level': typeDescriptor.level,
      'class': typeDescriptor.type.classTag,
      'role': ROLE_TYPE_TO_LABEL.get(typeDescriptor.type.role, 'None'),
    }
    
  def typeInfoToVehicleInfo(self, vo):
    # type: (VehicleArenaInfoVO) -> dict
    typeInfo = vo.vehicleType
    if typeInfo.compactDescr == 0: return None
    return {
      'tag': itemsVehicles.getItemByCompactDescr(typeInfo.compactDescr).name,
      'localizedName': typeInfo.shortName,
      'localizedShortName': typeInfo.name,
      'level': typeInfo.level,
      'class': typeInfo.classTag,
      'role': ROLE_TYPE_TO_LABEL.get(typeInfo.role, 'None'),
      'team': vo.team,
      'playerName': vo.player.name if vo.player else None,
      'playerId': vo.player.accountDBID if vo.player else None,
    }
    
  @withExceptionHandling(logger)
  def __onVehicleChanged(self, obj, *a, **k):
    vid = BigWorld.player().playerVehicleID
    vehicle = BigWorld.entity(vid) # type: Vehicle
    if not vehicle:
      return
    typeDescriptor = vehicle.typeDescriptor # type: VehicleDescriptor
    self.health.setValue(vehicle.health)
    
    self.vehicle.setValue(self.typeDescriptorToVehicleInfo(typeDescriptor))
    self.maxHealth.setValue(vehicle.maxHealth)
    self.isAlive.setValue(bool(vehicle.isAlive()))

  @withExceptionHandling(logger)
  def __onHealthChanged(self, obj, newHealth, oldHealth, attackerID, attackReasonID, *a, **k):
    vehId = obj.id
    if vehId == BigWorld.player().playerVehicleID:
      self.health.setValue(newHealth)
      self.maxHealth.setValue(obj.maxHealth)
      self.isAlive.setValue(bool(obj.isAlive()))
      
    if self.arenaDataProvider is None:
      return
    
    targetVehicle = self.arenaDataProvider.getVehicleInfo(vehId) # type: VehicleArenaInfoVO
    attackerVehicle = self.arenaDataProvider.getVehicleInfo(attackerID) # type: VehicleArenaInfoVO
      
    self.onDamageTrigger.trigger({
      'target': self.typeInfoToVehicleInfo(targetVehicle) if targetVehicle else None,
      'attacker': self.typeInfoToVehicleInfo(attackerVehicle) if attackerVehicle else None,
      'damage': max(0, oldHealth) - max(0, newHealth),
      'health': newHealth,
      'reason': ATTACK_REASONS[attackReasonID]
    })

  @withExceptionHandling(logger)
  def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo, *a, **k):
    self.arenaPeriod.setValue({
      'tag': ARENA_PERIOD_NAMES[period],
      'endTime': periodEndTime,
      'length': periodLength,
    })

  @withExceptionHandling(logger)
  def __onTeamBasePointsUpdate(self, team, baseID, points, timeLeft, invadersCnt, capturingStopped):
    current = self.teamBases.getValue()
    team = str(team)
    
    if not current:
      current = {}
    else:
      current = copy.deepcopy(current)
      
    teamData = current.get(team, None)
    
    if not teamData:
      teamData = []
      current[team] = teamData

    idx = -1
    for i, base in enumerate(teamData):
      if base['baseID'] == baseID:
        idx = i
        break
      
    newData = {
      'baseID': baseID,
      'points': points,
      'timeLeft': timeLeft,
      'invadersCount': invadersCnt,
      'capturingStopped': capturingStopped
    }
    
    if idx == -1:
      teamData.append(newData)
    else:
      teamData[idx] = newData
      
    self.teamBases.setValue(current)

  @withExceptionHandling(logger)
  def __onVehicleDamageStateUpdate(self, *a, **k):
    vehicle = BigWorld.entity(BigWorld.player().playerVehicleID)
    if not vehicle: return
    
    self.isAlive.setValue(bool(vehicle.isAlive()))

  @withExceptionHandling(logger)
  def __updateLoop(self):
    if self.started:
      self.battleLoopCallbackHandler = BigWorld.callback(0.1, self.__updateLoop)
    
    vehicle = BigWorld.entity(BigWorld.player().playerVehicleID) # type: Vehicle
    if vehicle:
      self.position.setValue([vehicle.position.x, vehicle.position.y, vehicle.position.z])
      self.rotation.setValue([vehicle.pitch, vehicle.yaw, vehicle.roll])
      
      if not vehicle.isStarted:
        self.speedInfo.setValue((0.0, 0.0))
        self.turretYaw.setValue(0.0)
        self.gunPitch.setValue(0.0)
      else:
        info = vehicle.speedInfo.value
        self.speedInfo.setValue((info[2], info[3]))
        
        turretYaw, gunPitch = decodeGunAngles(vehicle.gunAnglesPacked, vehicle.typeDescriptor.gun.pitchLimits['absolute'])
        self.turretYaw.setValue(turretYaw)
        self.gunPitch.setValue(gunPitch)
        
    
    player = BigWorld.player()
    if player.gunRotator:
      self.turretRotationSpeed.setValue(player.gunRotator.turretRotationSpeed)
    else:
      self.turretRotationSpeed.setValue(0.0)


onEnterWorld = Event()
onVehicleChanged = Event()
onHealthChanged = Event()
onVehicleDamageStateUpdate = Event()

@registerEvent(PlayerAvatar, 'onEnterWorld')
def playerAvatarOnEnterWorld(self, *a, **k):
  onEnterWorld(self, *a, **k)

@registerEvent(PlayerAvatar, 'onVehicleChanged')
def playerAvatarOnVehicleChanged(self, *a, **k):
  onVehicleChanged(self, *a, **k)

@registerEvent(Vehicle, 'onHealthChanged')
def vehicleOnHealthChanged(self, *a, **k):
  onHealthChanged(self, *a, **k)

@registerEvent(VehicleDamageState, 'update')
def vehicleDamageStateUpdate(self, *a, **k):
  onVehicleDamageStateUpdate(self, *a, **k)
