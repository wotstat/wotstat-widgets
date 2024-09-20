from Event import Event
from gui.Scaleform.framework.managers import context_menu
from gui.Scaleform.framework.managers.context_menu import AbstractContextMenuHandler

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
      BUTTONS.REMOVE: 'remove'
    })
    
  def _initFlashValues(self, ctx):
    self.wid = int(ctx.wid)
    self.isInResizing = bool(ctx.isInResizing)
    self.isLocked = bool(ctx.isLocked)
    self.isInBattle = bool(ctx.isInBattle)
    self.controlsVisible = bool(ctx.controlsVisible)
    
  @staticmethod
  def register():
    context_menu.registerHandlers(*[(WIDGET_CONTEXT_MENU, WidgetContextMenuHandler)])
  
  def _generateOptions(self, ctx=None):
    options = []
    
    if self.isLocked: options.insert(0, self._makeItem(BUTTONS.UNLOCK, 'Разблокировать перемещение', GREEN_TEXT))
    else: options.append(self._makeItem(BUTTONS.LOCK, 'Заблокировать перемещение'))
    
    if self.isInResizing: options.insert(0, self._makeItem(BUTTONS.END_RESIZE, 'Применить размер', GREEN_TEXT))
    else: options.append(self._makeItem(BUTTONS.RESIZE, 'Изменить размер'))
    
    options.append(self._makeItem(BUTTONS.CHANGE_URL, 'Изменить URL'))
    options.append(self._makeItem(BUTTONS.RELOAD, 'Перезагрузить'))
    
    if not self.isInBattle and not self.controlsVisible:
      options.insert(0, self._makeItem(BUTTONS.SHOW_CONTROLS, 'Показать элементы управления', GREEN_TEXT))
    else: options.append(self._makeItem(BUTTONS.HIDE_CONTROLS, 'Скрыть элементы управления'))
    
    options.append(self._makeItem(BUTTONS.CLEAR_DATA, 'Очистить данные', RED_TEXT))
    options.append(self._makeItem(BUTTONS.REMOVE, 'Удалить виджет', RED_TEXT))
      
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
    