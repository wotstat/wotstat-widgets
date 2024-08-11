from Account import PlayerAccount
import BigWorld
from PlayerEvents import g_playerEvents
from ..hook import registerEvent
from Event import Event
from gui.clans.clan_cache import g_clanCache

from ..DataProviderSDK import DataProviderSDK
from ..ExceptionHandling import withExceptionHandling

from . import logger

class PlayerProvider(object):
  
  def __init__(self, sdk):
    # type: (DataProviderSDK) -> None
    
    self.playerName = sdk.createState(['player', 'name'])
    self.playerId = sdk.createState(['player', 'id'])
    self.clanId = sdk.createState(['player', 'clanId'])
    self.clanTag = sdk.createState(['player', 'clanTag'])
    
    g_playerEvents.onAccountBecomePlayer += self.__onAccountBecomePlayer
    
    global onPlayerId
    onPlayerId += self.__onPlayerId
    
  @withExceptionHandling(logger)
  def __onAccountBecomePlayer(self):
    player = BigWorld.player() # type: PlayerAccount
    self.playerName.setValue(player.name)
    self.clanId.setValue(g_clanCache.clanDBID)
    self.clanTag.setValue(g_clanCache.clanAbbrev)
    
  @withExceptionHandling(logger)
  def __onPlayerId(self, playerId):
    self.playerId.setValue(playerId)
  

onPlayerId = Event()

@registerEvent(PlayerAccount, 'showGUI')
def playerAccount_showGUI(self, *a, **k):
  onPlayerId(self.databaseID)

  
    