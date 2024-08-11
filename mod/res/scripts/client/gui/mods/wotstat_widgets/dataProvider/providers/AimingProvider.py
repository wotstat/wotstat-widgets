from Avatar import PlayerAvatar
import BigWorld
from Event import Event
from VehicleGunRotator import VehicleGunRotator
from skeletons.account_helpers.settings_core import ISettingsCore
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
    
    self.sessionProvider.onBattleSessionStart += self.__onBattleSessionStart
    self.settingsCore.onSettingsChanged += self.__applySettings
    
    global onUpdateGunMarker, onSetShotPosition, onEnableServerAim, onAutoAim, onEnterWorld, onVehicleGunRotatorStart
    onUpdateGunMarker += self.__onUpdateGunMarker
    onSetShotPosition += self.__onSetShotPosition
    onEnableServerAim += self.__onEnableServerAim
    onVehicleGunRotatorStart += self.__onVehicleGunRotatorStart
    onAutoAim += self.__autoAim
    onEnterWorld += self.__onEnterWorld
    
  @withExceptionHandling(logger)
  def __onBattleSessionStart(self, *args, **kwargs):
    self.isAutoAim.setValue(False)
    BigWorld.player().enableServerAim(True)
    self.isServerAim.setValue(bool(self.settingsCore.getSetting('useServerAim')))
    
  @withExceptionHandling(logger)
  def __onEnterWorld(self, *args, **kwargs):
    self.isServerAim.setValue(bool(self.settingsCore.getSetting('useServerAim')))
    
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
    
    player = BigWorld.player() # type: PlayerAvatar
    self.idealDispersion.setValue(player.vehicleTypeDescriptor.gun.shotDispersionAngle)
    
  # set server
  @withExceptionHandling(logger)
  def __onSetShotPosition(self, obj, vehicleID, shotPos, shotVec, dispersionAngle, *args, **kwargs):
    self.markerServerPosition = obj._VehicleGunRotator__getGunMarkerPosition(
      shotPos, shotVec, [dispersionAngle, dispersionAngle, dispersionAngle, dispersionAngle])[0]

    self.markerServerDispersion = dispersionAngle
    self.serverDispersion.setValue(dispersionAngle)
    
    player = BigWorld.player() # type: PlayerAvatar
    self.idealDispersion.setValue(player.vehicleTypeDescriptor.gun.shotDispersionAngle)
    
  @withExceptionHandling(logger)
  def __onEnableServerAim(self, *args, **kwargs):
    self.isServerAim.setValue(bool(self.settingsCore.getSetting('useServerAim')))
    
  @withExceptionHandling(logger)
  def __autoAim(self, *args, **kwargs):
    self.isAutoAim.setValue(BigWorld.player().autoAimVehicle is not None)

  @withExceptionHandling(logger)
  def __onVehicleGunRotatorStart(self, *args, **kwargs):
    self.isServerAim.setValue(bool(self.settingsCore.getSetting('useServerAim')))
    
  def __applySettings(self, diff):
    if 'useServerAim' in diff:
      self.isServerAim.setValue(bool(diff['useServerAim']))
  

onVehicleGunRotatorStart = Event()
onUpdateGunMarker = Event()
onSetShotPosition = Event()
onEnableServerAim = Event()
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
