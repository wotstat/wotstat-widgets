from ..DataProviderSDK import DataProviderSDK
from helpers import dependency
from gui.battle_control.battle_constants import PERSONAL_EFFICIENCY_TYPE
from skeletons.gui.battle_session import IBattleSessionProvider

from ..ExceptionHandling import withExceptionHandling

from . import logger

class TotalEfficiencyProvider(object):
  sessionProvider = dependency.descriptor(IBattleSessionProvider) # type: IBattleSessionProvider
  
  def __init__(self, sdk):
    # type: (DataProviderSDK) -> None
    
    self.damage = sdk.createState(['battle', 'efficiency', 'damage'], 0)
    self.assist = sdk.createState(['battle', 'efficiency', 'assist'], 0)
    self.blocked = sdk.createState(['battle', 'efficiency', 'blocked'], 0)
    self.stun = sdk.createState(['battle', 'efficiency', 'stun'], 0)
    
    self.sessionProvider.onBattleSessionStart += self.__onBattleSessionStart
    self.sessionProvider.onBattleSessionStop += self.__onBattleSessionStop
    
    self.vehicleState = None
    self.arenaDP = None
    
  @withExceptionHandling(logger)
  def __onBattleSessionStart(self):
    self.vehicleState = self.sessionProvider.shared.vehicleState
    self.arenaDP = self.sessionProvider.getArenaDP()
    
    if self.sessionProvider.shared.personalEfficiencyCtrl:
      self.sessionProvider.shared.personalEfficiencyCtrl.onTotalEfficiencyUpdated += self.__onTotalEfficiencyReceived
    self.damage.setValue(0)
    self.assist.setValue(0)
    self.blocked.setValue(0)
    self.stun.setValue(0)
    
  @withExceptionHandling(logger)
  def __onBattleSessionStop(self):
    if self.sessionProvider.shared.personalEfficiencyCtrl:
      self.sessionProvider.shared.personalEfficiencyCtrl.onTotalEfficiencyUpdated += self.__onTotalEfficiencyReceived
      
    self.damage.setValue(0)
    self.assist.setValue(0)
    self.blocked.setValue(0)
    self.stun.setValue(0)

  @withExceptionHandling(logger)
  def __onTotalEfficiencyReceived(self, diff):
    if not self.vehicleState or not self.arenaDP: return
    if self.vehicleState.getControllingVehicleID() != self.arenaDP.getPlayerVehicleID(): return
    
    if PERSONAL_EFFICIENCY_TYPE.DAMAGE in diff:
      self.damage.setValue(diff[PERSONAL_EFFICIENCY_TYPE.DAMAGE])
      
    if PERSONAL_EFFICIENCY_TYPE.ASSIST_DAMAGE in diff:
      self.assist.setValue(diff[PERSONAL_EFFICIENCY_TYPE.ASSIST_DAMAGE])
      
    if PERSONAL_EFFICIENCY_TYPE.BLOCKED_DAMAGE in diff:
      self.blocked.setValue(diff[PERSONAL_EFFICIENCY_TYPE.BLOCKED_DAMAGE])
      
    if PERSONAL_EFFICIENCY_TYPE.STUN in diff:
      self.stun.setValue(diff[PERSONAL_EFFICIENCY_TYPE.STUN])