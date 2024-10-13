from Avatar import PlayerAvatar
import BigWorld
from Event import Event
from VehicleGunRotator import VehicleGunRotator
from skeletons.account_helpers.settings_core import ISettingsCore
from account_helpers.settings_core import settings_constants
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IGameSessionController
from skeletons.gui.shared import IItemsCache
from ..DataProviderSDK import DataProviderSDK
from helpers import dependency

from ..hook import registerEvent
from ..ExceptionHandling import withExceptionHandling
from . import logger

class AimingProvider(object):

  gameSession = dependency.descriptor(IGameSessionController) # type: IGameSessionController
  sessionProvider = dependency.descriptor(IBattleSessionProvider) # type: IBattleSessionProvider
  itemsCache = dependency.descriptor(IItemsCache) # type: IItemsCache
  settingsCore = dependency.instance(ISettingsCore) # type: ISettingsCore
  
  def __init__(self, sdk):
    # type: (DataProviderSDK) -> None
    
    self.isAutoAim = sdk.createState(['battle', 'aiming', 'isAutoAim'])
    self.isServerAim = sdk.createState(['battle', 'aiming', 'isServerAim'])
    self.idealDispersion = sdk.createState(['battle', 'aiming', 'idealDispersion'])
    self.serverDispersion = sdk.createState(['battle', 'aiming', 'serverDispersion'])
    self.clientDispersion = sdk.createState(['battle', 'aiming', 'clientDispersion'])
    self.aimingTime = sdk.createState(['battle', 'aiming', 'aimingTime'])
    
    self.sessionProvider.onBattleSessionStart += self.__onBattleSessionStart
    self.settingsCore.onSettingsChanged += self.__applySettings
    
    global onUpdateGunMarker, onSetShotPosition, onEnableServerAim, onAutoAim, onEnterWorld, onVehicleGunRotatorStart, onUpdateTargetingInfo
    onUpdateGunMarker += self.__onUpdateGunMarker
    onSetShotPosition += self.__onSetShotPosition
    onEnableServerAim += self.__onEnableServerAim
    onVehicleGunRotatorStart += self.__onVehicleGunRotatorStart
    onAutoAim += self.__autoAim
    onEnterWorld += self.__onEnterWorld
    onUpdateTargetingInfo += self.__onUpdateTargetingInfo
    
  @withExceptionHandling(logger)
  def __onBattleSessionStart(self, *args, **kwargs):
    self.isAutoAim.setValue(False)
    BigWorld.player().enableServerAim(True)
    self.isServerAim.setValue(self.isEnableServerAim())
    
  @withExceptionHandling(logger)
  def __onEnterWorld(self, *args, **kwargs):
    self.isServerAim.setValue(self.isEnableServerAim())
    
    player = BigWorld.player() # type: PlayerAvatar
    if hasattr(player.vehicleTypeDescriptor, 'gun'):
      disp = player.vehicleTypeDescriptor.gun.shotDispersionAngle
      self.idealDispersion.setValue(disp)
      self.serverDispersion.setValue(disp)
      self.clientDispersion.setValue(disp)
  
  # set client
  @withExceptionHandling(logger)
  def __onUpdateGunMarker(self, obj, *args, **kwargs):
    vehicle = obj._avatar.getVehicleAttached()
    if vehicle is None: return
    if vehicle.id != BigWorld.player().playerVehicleID: return
    
    shotPos, shotVec = obj.getCurShotPosition()
    self.markerClientPosition = obj._VehicleGunRotator__getGunMarkerPosition(
      shotPos, shotVec, obj._VehicleGunRotator__dispersionAngles)[0]

    self.markerClientDispersion = obj._VehicleGunRotator__dispersionAngles[0]
    self.clientDispersion.setValue(self.markerClientDispersion)
    
  # set server
  @withExceptionHandling(logger)
  def __onSetShotPosition(self, obj, vehicleID, shotPos, shotVec, dispersionAngle, *args, **kwargs):
    self.markerServerPosition = obj._VehicleGunRotator__getGunMarkerPosition(
      shotPos, shotVec, [dispersionAngle, dispersionAngle, dispersionAngle, dispersionAngle])[0]

    self.markerServerDispersion = dispersionAngle
    self.serverDispersion.setValue(dispersionAngle)
  
  @withExceptionHandling(logger)
  def __onUpdateTargetingInfo(self, obj, entityId, *a, **k):
    # type: (PlayerAvatar, int) -> None
    if entityId != obj.playerVehicleID: return
    
    dispersionInfo = obj._PlayerAvatar__dispersionInfo
    if not dispersionInfo or len(dispersionInfo) < 4: return logger.warn('AimingProvider -> dispersionInfo is invalid')
    shotDispMultiplierFactor = dispersionInfo[0]
    aimingTime = dispersionInfo[4]
    
    idealDispersion = obj.vehicleTypeDescriptor.gun.shotDispersionAngle * shotDispMultiplierFactor
    
    self.idealDispersion.setValue(idealDispersion)
    self.aimingTime.setValue(aimingTime)
    
  @withExceptionHandling(logger)
  def __onEnableServerAim(self, *args, **kwargs):
    self.isServerAim.setValue(self.isEnableServerAim())
    
  @withExceptionHandling(logger)
  def __autoAim(self, *args, **kwargs):
    self.isAutoAim.setValue(BigWorld.player().autoAimVehicle is not None)

  @withExceptionHandling(logger)
  def __onVehicleGunRotatorStart(self, *args, **kwargs):
    self.isServerAim.setValue(self.isEnableServerAim())
    
  def __applySettings(self, diff):
    if settings_constants.GAME.ENABLE_SERVER_AIM in diff:
      self.isServerAim.setValue(True if diff[settings_constants.GAME.ENABLE_SERVER_AIM] else False)
      
  def isEnableServerAim(self):
    return True if self.settingsCore.getSetting(settings_constants.GAME.ENABLE_SERVER_AIM) else False
  

onVehicleGunRotatorStart = Event()
onUpdateGunMarker = Event()
onSetShotPosition = Event()
onEnableServerAim = Event()
onUpdateTargetingInfo = Event()
onEnterWorld = Event()
onAutoAim = Event()

@registerEvent(VehicleGunRotator, '_VehicleGunRotator__updateGunMarker')
def updateGunMarker(self, *a, **k):
  onUpdateGunMarker(self, *a, **k)
  
@registerEvent(VehicleGunRotator, 'setShotPosition')
def setShotPosition(self, *a, **k):
  onSetShotPosition(self, *a, **k)
  
@registerEvent(VehicleGunRotator, 'start')
def vehicleGunRotatorStart(self, *a, **k):
  onVehicleGunRotatorStart(self, *a, **k)
  
@registerEvent(PlayerAvatar, 'enableServerAim')
def enableServerAim(self, *a, **k):
  onEnableServerAim(self, *a, **k)
  
@registerEvent(PlayerAvatar, 'autoAim')
def autoAim(self, *a, **k):
  onAutoAim(self, *a, **k)

@registerEvent(PlayerAvatar, 'onEnterWorld')
def enterWorld(self, *a, **k):
  onEnterWorld(self, *a, **k)
  
@registerEvent(PlayerAvatar, 'updateTargetingInfo')
def updateTargetingInfo(self, *a, **k):
  onUpdateTargetingInfo(self, *a, **k)


