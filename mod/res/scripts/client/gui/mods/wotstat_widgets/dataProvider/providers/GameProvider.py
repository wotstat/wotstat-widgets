import BigWorld
from Event import Event
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.shared.utils import IHangarSpace
from ..DataProviderSDK import DataProviderSDK
from ..crossGameUtils import readClientServerVersion
from helpers import dependency, getClientLanguage
from constants import AUTH_REALM, SERVER_TICK_LENGTH
from gui.Scaleform.daapi.view.login.LoginView import LoginView
import BattleReplay

from ..hook import registerEvent
from ..ExceptionHandling import withExceptionHandling
from . import logger
  
class GAME_STATE:
  LOADING = 'loading'
  BATTLE = 'battle'
  HANGAR = 'hangar'
  LOGIN = 'login'
  
class GameProvider(object):

  connectionMgr = dependency.descriptor(IConnectionManager) # type: IConnectionManager
  sessionProvider = dependency.descriptor(IBattleSessionProvider) # type: IBattleSessionProvider
  hangarSpace = dependency.descriptor(IHangarSpace) # type: IHangarSpace
  
  def __init__(self, sdk):
    # type: (DataProviderSDK) -> None
    sdk.createState(['game', 'dataProviderVersion'], BigWorld.wotstat_dataProvider.version)
    self.version = sdk.createState(['game', 'version'], readClientServerVersion()[1])
    self.region = sdk.createState(['game', 'region'], AUTH_REALM)
    self.language = sdk.createState(['game', 'language'], getClientLanguage())
    self.server = sdk.createState(['game', 'server'], None)
    self.state = sdk.createState(['game', 'state'], GAME_STATE.LOADING)
    self.serverTime = sdk.createState(['game', 'serverTime'], None)
    self.ping = sdk.createState(['game', 'ping'], None)
    self.fps = sdk.createState(['game', 'fps'], None)
    self.isInReplay = sdk.createState(['game', 'isInReplay'], False)
    
    self.connectionMgr.onConnected += self.__onConnected
    self.sessionProvider.onBattleSessionStart += self.__onBattleSessionStart
    self.hangarSpace.onSpaceCreate += self.__onHangarSpaceCreate
    
    global onLoginPopulate
    onLoginPopulate += self.__onLoginPopulate
    
    self.__serverTimeUpdateLoop()
    self.__pingFpsUpdateLoop()
    
  @withExceptionHandling(logger)
  def __onConnected(self, *args, **kwargs):
    self.server.setValue(self.connectionMgr.serverUserName)
    self.isInReplay.setValue(BattleReplay.isPlaying())
    
  @withExceptionHandling(logger)
  def __onBattleSessionStart(self):
    self.state.setValue(GAME_STATE.BATTLE)
    self.isInReplay.setValue(BattleReplay.isPlaying())
    
  @withExceptionHandling(logger)
  def __onLoginPopulate(self):
    self.state.setValue(GAME_STATE.LOGIN)
    
  @withExceptionHandling(logger)
  def __onHangarSpaceCreate(self):
    self.state.setValue(GAME_STATE.HANGAR)
    self.isInReplay.setValue(BattleReplay.isPlaying())
    
  @withExceptionHandling(logger)
  def __serverTimeUpdateLoop(self):
    BigWorld.callback(1, self.__serverTimeUpdateLoop)
    self.serverTime.setValue(BigWorld.serverTime())
    
  @withExceptionHandling(logger)
  def __pingFpsUpdateLoop(self):
    BigWorld.callback(0.1, self.__pingFpsUpdateLoop)
    self.ping.setValue(max(BigWorld.LatencyInfo().value[3] - 0.5 * SERVER_TICK_LENGTH, 0))
    self.fps.setValue(BigWorld.getFPS()[1])

onLoginPopulate = Event()
  
@registerEvent(LoginView, '_populate')
def loginPopulate(self, *a, **k):
  onLoginPopulate()