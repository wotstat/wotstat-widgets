from functools import partial
from Account import PlayerAccount
import BigWorld
from CurrentVehicle import g_currentVehicle
from items import vehicles

from PlayerEvents import g_playerEvents

from ..DataProviderSDK import DataProviderSDK
from ..ExceptionHandling import withExceptionHandling
from . import logger


CACHE_TIME = 60.0 * 10 # 10 minutes
REQUEST_MIN_DELAY = 1.0

class MoeInfoProvider(object):
  def __init__(self, sdk):
    # type: (DataProviderSDK) -> None
    
    self.moeCache = {}
    self.currentDescriptor = None
    self.lastResponseTime = 0.0
    
    self.current = sdk.createState(['moeInfo', 'current'], False)
    self.isAvailable = sdk.createState(['moeInfo', 'isAvailable'])

    try:
      from AccountCommands import CMD_GET_VEHICLE_DAMAGE_DISTRIBUTION
      self.isAvailable.setValue(True)
    except ImportError:
      self.isAvailable.setValue(False)
      return

    g_playerEvents.onAccountBecomePlayer += self.__onAccountBecomePlayer
    g_playerEvents.onAccountBecomeNonPlayer += self.__onAccountBecomeNonPlayer
    
  @withExceptionHandling(logger)
  def __onAccountBecomePlayer(self):
    g_currentVehicle.onChanged += self.__updateMoeInfo
    
  @withExceptionHandling(logger)
  def __onAccountBecomeNonPlayer(self):
    g_currentVehicle.onChanged -= self.__updateMoeInfo
    
  def __updateMoeInfo(self, *a, **k):
    if g_currentVehicle and g_currentVehicle.item:
      self.currentDescriptor = g_currentVehicle.item.intCD
      self.__updateCurrentInfo()

  def __setValue(self, value):
    if value is None: 
      self.current.setValue(None)
      return
    
    if value.get('vehicleTag', None) is None:
      self.current.setValue(None)
      return
    
    self.current.setValue({
      'vehicleTag': value.get('vehicleTag', None),
      'battleCount': value.get('battleCount', 0),
      'damageBetterThanNPercent': value.get('damageBetterThanNPercent', None),
    })

  def __updateCurrentInfo(self):
    def callback(descriptor, requestID, responseID, errorStr, ext=None):
      self.lastResponseTime = BigWorld.time()
      
      if ext is None:
        self.moeCache[descriptor] = {
          'time': BigWorld.time(),
          'vehicleTag': None,
          'battleCount': None,
          'damageBetterThanNPercent': None,
        }
      else:
        self.moeCache[descriptor] = {
          'time': BigWorld.time(),
          'vehicleTag': vehicles.getItemByCompactDescr(descriptor).name,
          'battleCount': ext.get('battleCount', 0),
          'damageBetterThanNPercent': ext.get('damageBetterThanNPercent', None),
        }
      
      if descriptor != self.currentDescriptor:
        return
      
      self.__setValue(self.moeCache[descriptor])
      
    if not self.currentDescriptor: return
    
    if not BigWorld.player() or not isinstance(BigWorld.player(), PlayerAccount): return

    if self.currentDescriptor in self.moeCache and BigWorld.time() - self.moeCache[self.currentDescriptor].get('time', 0) < CACHE_TIME:
      self.__setValue(self.moeCache[self.currentDescriptor])
      return

    if self.lastResponseTime + REQUEST_MIN_DELAY < BigWorld.time():
      from AccountCommands import CMD_GET_VEHICLE_DAMAGE_DISTRIBUTION
      BigWorld.player()._doCmdInt(
        CMD_GET_VEHICLE_DAMAGE_DISTRIBUTION,
        self.currentDescriptor,
        partial(callback, self.currentDescriptor)
      )
    else:
      BigWorld.callback(BigWorld.time() - self.lastResponseTime + REQUEST_MIN_DELAY, self.__updateCurrentInfo)
