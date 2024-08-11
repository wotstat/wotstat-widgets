from skeletons.gui.game_control import IGameSessionController
from skeletons.gui.shared import IItemsCache
from ..DataProviderSDK import DataProviderSDK
from constants import PREMIUM_TYPE
from helpers import dependency

from ..ExceptionHandling import withExceptionHandling

from . import logger

class AccountProvider(object):

  gameSession = dependency.descriptor(IGameSessionController) # type: IGameSessionController
  itemsCache = dependency.descriptor(IItemsCache) # type: IItemsCache
  
  def __init__(self, sdk):
    # type: (DataProviderSDK) -> None
    
    self.credits = sdk.createState(['account', 'credits'])
    self.gold = sdk.createState(['account', 'gold'])
    self.crystal = sdk.createState(['account', 'crystal'])
    self.freeXp = sdk.createState(['account', 'freeXp'])
    self.premium = sdk.createState(['account', 'premium'])
    
    self.itemsCache.onSyncCompleted += self.__updateItemsCache
    
  @withExceptionHandling(logger)
  def __updateItemsCache(self, *args, **kwargs):
    stats = self.itemsCache.items.stats
    self.credits.setValue(stats.actualCredits)
    self.gold.setValue(stats.actualGold)
    self.crystal.setValue(stats.actualCrystal)
    self.freeXp.setValue(stats.actualFreeXP)
    
    premium = self.itemsCache.items.stats.premiumInfo
    basic = premium.get(PREMIUM_TYPE.BASIC, None)
    plus = premium.get(PREMIUM_TYPE.PLUS, None)
    vip = premium.get(PREMIUM_TYPE.VIP, None)
    self.premium.setValue({
      'basic': { 'active': basic['active'], 'expiration': basic['expiryTime'] } if basic else None,
      'plus': { 'active': plus['active'], 'expiration': plus['expiryTime'] } if plus else None,
      'vip': { 'active': vip['active'], 'expiration': vip['expiryTime'] } if vip else None,
    })
  