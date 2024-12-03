from Event import Event
from gui.Scaleform.framework.managers import context_menu
from gui.Scaleform.framework.managers.context_menu import AbstractContextMenuHandler
from .WidgetStorage import POSITION_MODE, LAYER

from ..common.i18n import t

WIDGET_CONTEXT_MENU = 'WOTSTAT_WIDGET_CONTEXT_MENU'
RED_COLOR = 16726832
GREEN_COLOR = 3458905

RED_TEXT = { 'textColor': RED_COLOR }
GREEN_TEXT = { 'textColor': GREEN_COLOR }

class BUTTONS(object):
  LOCK = 'LOCK'
  UNLOCK = 'UNLOCK'
  RESIZE = 'RESIZE'
  END_RESIZE = 'END_RESIZE'
  CHANGE_URL = 'CHANGE_URL'
  RELOAD = 'RELOAD'
  HIDE_CONTROLS = 'HIDE_CONTROLS'
  SHOW_CONTROLS = 'SHOW_CONTROLS'
  CLEAR_DATA = 'CLEAR_DATA'
  REMOVE = 'REMOVE'
  SEND_TO_TOP_PLAN = 'SEND_TO_TOP_PLAN'
  POSITION_SAME = 'POSITION_SAME'
  POSITION_HANGAR_BATTLE = 'POSITION_HANGAR_BATTLE'
  POSITION_HANGAR_SNIPER_ARCADE = 'POSITION_HANGAR_SNIPER_ARCADE'
  LAYER_DEFAULT = 'LAYER_DEFAULT'
  LAYER_TOP = 'LAYER_TOP'

class WidgetContextMenuHandler(AbstractContextMenuHandler):
  
  onEvent = Event()
    
  def __init__(self, cmProxy, ctx=None):
    super(WidgetContextMenuHandler, self).__init__(cmProxy, ctx, {
      BUTTONS.LOCK: 'lock',
      BUTTONS.UNLOCK: 'unlock',
      BUTTONS.RESIZE: 'resize',
      BUTTONS.END_RESIZE: 'endResize',
      BUTTONS.CHANGE_URL: 'changeUrl',
      BUTTONS.RELOAD: 'reload',
      BUTTONS.HIDE_CONTROLS: 'hideControls',
      BUTTONS.SHOW_CONTROLS: 'showControls',
      BUTTONS.CLEAR_DATA: 'clearData',
      BUTTONS.REMOVE: 'remove',
      BUTTONS.SEND_TO_TOP_PLAN: 'sendToTopPlan',
      BUTTONS.POSITION_SAME: 'positionSame',
      BUTTONS.POSITION_HANGAR_BATTLE: 'positionHangarBattle',
      BUTTONS.POSITION_HANGAR_SNIPER_ARCADE: 'positionHangarSniperArcade',
      BUTTONS.LAYER_DEFAULT: 'layerDefault',
      BUTTONS.LAYER_TOP: 'layerTop',
    })
    
  def _initFlashValues(self, ctx):
    self.wid = int(ctx.wid)
    self.isInResizing = bool(ctx.isInResizing)
    self.isLocked = bool(ctx.isLocked)
    self.isInBattle = bool(ctx.isInBattle)
    self.isControlsAlwaysHidden = bool(ctx.isControlsAlwaysHidden)
    self.isReadyToClearData = bool(ctx.isReadyToClearData)
    self.isTopPlan = bool(ctx.isTopPlan)
    self.hangarOnly = bool(ctx.hangarOnly)
    self.layer = ctx.layer
    self.positionMode = ctx.positionMode
    
  @staticmethod
  def register():
    context_menu.registerHandlers(*[(WIDGET_CONTEXT_MENU, WidgetContextMenuHandler)])
  
  def _generateOptions(self, ctx=None):
    options = []
    
    if self.isLocked: options.insert(0, self._makeItem(BUTTONS.UNLOCK, t('context.unlock'), GREEN_TEXT))
    else: options.append(self._makeItem(BUTTONS.LOCK, t('context.lock')))
    
    if self.isInResizing: options.insert(0, self._makeItem(BUTTONS.END_RESIZE, t('context.endResize'), GREEN_TEXT))
    else: options.append(self._makeItem(BUTTONS.RESIZE, t('context.resize')))
    
    if not self.isInBattle:
      options.append(self._makeItem(BUTTONS.CHANGE_URL, t('context.changeUrl')))
      
    options.append(self._makeItem(BUTTONS.RELOAD, t('context.reload')))
    
    if self.isControlsAlwaysHidden: options.insert(0, self._makeItem(BUTTONS.SHOW_CONTROLS, t('context.showControls'), GREEN_TEXT)) 
    else: options.append(self._makeItem(BUTTONS.HIDE_CONTROLS, t('context.hideControls')))
    
    if not self.isTopPlan: options.append(self._makeItem(BUTTONS.SEND_TO_TOP_PLAN, t('context.sendToTopPlan')))
    
    if not self.hangarOnly:
      currentPositionMode = t('context.position.hangarBattle')
      if self.positionMode == POSITION_MODE.SAME: currentPositionMode = t('context.position.same')
      elif self.positionMode == POSITION_MODE.HANGAR_SNIPER_ARCADE: currentPositionMode = t('context.position.hangarSniperArcade')
    
      options.append(self._makeItem('position_mode_sub', t('context.position') % currentPositionMode, optSubMenu=[
        self._makeItem(BUTTONS.POSITION_SAME, t('context.position.same')),
        self._makeItem(BUTTONS.POSITION_HANGAR_BATTLE, t('context.position.hangarBattle')),
        self._makeItem(BUTTONS.POSITION_HANGAR_SNIPER_ARCADE, t('context.position.hangarSniperArcade')),
      ]))
    
    currentLayer = t('context.layer.default')
    if self.layer == LAYER.LAYER_TOP: currentLayer = t('context.layer.top')
    options.append(self._makeItem('layer_sub', t('context.layer') % currentLayer, optSubMenu=[
      self._makeItem(BUTTONS.LAYER_DEFAULT, t('context.layer.default')),
      self._makeItem(BUTTONS.LAYER_TOP, t('context.layer.top')),
    ]))
    
    if self.isReadyToClearData:
      options.append(self._makeItem('clear_data_sub', t('context.clearData'), RED_TEXT, [
      self._makeItem(BUTTONS.CLEAR_DATA, t('context.clearData.apply'), RED_TEXT)
    ]))

    options.append(self._makeItem(BUTTONS.REMOVE, t('context.remove'), RED_TEXT))
      
    return options
  
  def callEvent(self, eventName): 
    self.onEvent((eventName, self.wid))
    
  def lock(self): self.callEvent(BUTTONS.LOCK)
  def unlock(self): self.callEvent(BUTTONS.UNLOCK)
  def resize(self): self.callEvent(BUTTONS.RESIZE)
  def endResize(self): self.callEvent(BUTTONS.END_RESIZE)
  def changeUrl(self): self.callEvent(BUTTONS.CHANGE_URL)
  def reload(self): self.callEvent(BUTTONS.RELOAD)
  def hideControls(self): self.callEvent(BUTTONS.HIDE_CONTROLS)
  def showControls(self): self.callEvent(BUTTONS.SHOW_CONTROLS)
  def clearData(self): self.callEvent(BUTTONS.CLEAR_DATA)
  def remove(self): self.callEvent(BUTTONS.REMOVE)
  def sendToTopPlan(self): self.callEvent(BUTTONS.SEND_TO_TOP_PLAN)
  def positionSame(self): self.callEvent(BUTTONS.POSITION_SAME)
  def positionHangarBattle(self): self.callEvent(BUTTONS.POSITION_HANGAR_BATTLE)
  def positionHangarSniperArcade(self): self.callEvent(BUTTONS.POSITION_HANGAR_SNIPER_ARCADE)
  def layerDefault(self): self.callEvent(BUTTONS.LAYER_DEFAULT)
  def layerTop(self): self.callEvent(BUTTONS.LAYER_TOP)
    