import json
import os
import errno

import BigWorld
from Singleton import Singleton
from uuid import uuid4
from typing import Dict

from aih_constants import CTRL_MODE_NAME  # noqa: F401

from ..common.Logger import Logger
from ..constants import ACTIVE_WIDGETS_PATH

def setup():
  dir = os.path.dirname(ACTIVE_WIDGETS_PATH)
  if not os.path.isdir(dir):
    os.makedirs(dir)

setup()


class POSITION_MODE(object):
  NOT_SET = 'NOT_SET'
  SAME = 'SAME'
  HANGAR_BATTLE = 'HANGAR_BATTLE'
  HANGAR_SNIPER_ARCADE = 'HANGAR_SNIPER_ARCADE'
  
class LAYER(object):
  LAYER_TOP = 'TOP'
  LAYER_DEFAULT = 'DEFAULT'

class WidgetInfo(object):
  
  class PositionState(object):
    def __init__(self):
      self.width = 0
      self.height = 0
      self.position = [0, 0]
      self.isHidden = False
      self.isLocked = False
      self.isControlsAlwaysHidden = False
      self.isTouched = False
      
    def toDict(self):
      return {
        "width": self.width,
        "height": self.height,
        "position": self.position,
        "isHidden": self.isHidden,
        "isLocked": self.isLocked,
        "isControlsAlwaysHidden": self.isControlsAlwaysHidden,
        "isTouched": self.isTouched
      }
      
    def fromDict(self, data):
      self.width = data.get("width", 0)
      self.height = data.get("height", 0)
      self.position = data.get("position", [data.get("x", 0), data.get("y", 0)])
      self.isHidden = data.get("isHidden", False)
      self.isLocked = data.get("isLocked", False)
      self.isControlsAlwaysHidden = data.get("isControlsAlwaysHidden", False)
      self.isTouched = data.get("isTouched", False)
  
  class PositionBattleState(PositionState):
    def __init__(self):
      super(WidgetInfo.PositionBattleState, self).__init__()
      self.sniperPosition = None
      self.artyPosition = None
      self.strategicPosition = None
      
    def toDict(self):
      data = super(WidgetInfo.PositionBattleState, self).toDict()
      data["sniperPosition"] = self.sniperPosition
      data["artyPosition"] = self.artyPosition
      data["strategicPosition"] = self.strategicPosition
      return data
      
    def fromDict(self, data):
      super(WidgetInfo.PositionBattleState, self).fromDict(data)
      self.sniperPosition = data.get("sniperPosition", None)
      self.artyPosition = data.get("artyPosition", None)
      self.strategicPosition = data.get("strategicPosition", None)
    
  def __init__(self):
    self.uuid = ""
    self.wid = None
    self.url = ""
    self.hangar = WidgetInfo.PositionState()
    self.battle = WidgetInfo.PositionBattleState()
    self.order = 0
    self.flags = 0
    self.positionMode = POSITION_MODE.NOT_SET
    self.layer = LAYER.LAYER_DEFAULT
  
  def getPreferredPosition(self, battle, mode=None):
  # type: (bool, str) -> List[int]
    
    hangarState = self.battle if not self.hangar.isTouched and self.battle.isTouched else self.hangar
    if not battle: return hangarState.position
    
    state = self.battle

    if not state.isTouched:
      return self.hangar.position
    
    if self.positionMode == POSITION_MODE.SAME:
      return hangarState.position
    
    if self.positionMode == POSITION_MODE.HANGAR_BATTLE:
      return state.position
    
    if mode == CTRL_MODE_NAME.SNIPER:
      return state.sniperPosition or state.position
    
    if mode == CTRL_MODE_NAME.ARTY:
      return state.artyPosition or state.strategicPosition or state.position
    
    if mode == CTRL_MODE_NAME.STRATEGIC:
      return state.strategicPosition or state.artyPosition or state.position
    
    return state.position
  
  def toSerializable(self):
    return {
      "uuid": self.uuid,
      "url": self.url,
      "positionMode": self.positionMode,
      "layer": self.layer,
      "hangar": self.hangar.toDict(),
      "battle": self.battle.toDict(),
      "order": self.order,
    }
  
  @staticmethod
  def fromSerializable(data):
    w = WidgetInfo()

    w.uuid = data["uuid"]
    w.url = data["url"]
    w.positionMode = data.get("positionMode", POSITION_MODE.NOT_SET)
    w.layer = data.get("layer", LAYER.LAYER_DEFAULT)
    w.order = data.get("order", 0)
    
    hangar = data.get("hangar", {})
    w.hangar.fromDict(hangar)
    
    battle = data.get("battle", {})
    w.battle.fromDict(battle)
    
    return w

logger = Logger.instance()
UNDEFINED = object()

class WidgetStorage(Singleton):

  @staticmethod
  def instance():
    return WidgetStorage()
  

  _isChanged = False
  _widgets = {} # type: Dict[str, WidgetInfo]
  _widgetsByWid = {} # type: Dict[str, WidgetInfo]
  
  def _singleton_init(self):
    self._load()
    self._saveLoop()
  
  def getAllWidgets(self):
    return sorted(self._widgets.values(), key=lambda x: x.order)
  
  def getWidgetByWid(self, wid):
    return self._widgetsByWid.get(wid, None)
  
  def addWidget(self, wid, url, width=100, height=100, x=-1, y=-1, isHidden=False, isLocked=False, isControlsAlwaysHidden=False):
    uuid = str(uuid4())
    
    widget = WidgetInfo()
    widget.uuid = uuid
    widget.wid = wid
    widget.url = url
    
    widget.battle.width = width
    widget.battle.height = height
    widget.battle.position = [x, y]
    widget.battle.isHidden = isHidden
    widget.battle.isLocked = isLocked
    widget.battle.isControlsAlwaysHidden = isControlsAlwaysHidden
    
    widget.hangar.width = width
    widget.hangar.height = height
    widget.hangar.position = [x, y]
    widget.hangar.isHidden = isHidden
    widget.hangar.isLocked = isLocked
    widget.hangar.isControlsAlwaysHidden = isControlsAlwaysHidden
    
    self._widgets[uuid] = widget
    self._widgetsByWid[wid] = widget
    
    maxOrder = max([w.order for w in self._widgets.values()])
    widget.order = maxOrder + 1

    self._isChanged = True

  def removeWidget(self, wid):
    for key, widget in self._widgets.items():
      if widget.wid == wid:
        del self._widgets[key]
        break

    del self._widgetsByWid[wid]

    self._isChanged = True
      
  def updateWidget(self, wid, fromBattle, url=UNDEFINED, positionMode=UNDEFINED, layer=UNDEFINED,
                   width=UNDEFINED, height=UNDEFINED,
                   position=UNDEFINED, sniperPosition=UNDEFINED, artyPosition=UNDEFINED, strategicPosition=UNDEFINED,
                   isHidden=UNDEFINED, isLocked=UNDEFINED, isControlsAlwaysHidden=UNDEFINED, flags=UNDEFINED):
    widget = self._widgetsByWid.get(wid, None)
    if widget is None: return

    def update(param, value, fromBattle=fromBattle):
      if param is not None and value is not UNDEFINED:
        target = widget
        
        if fromBattle == True: target = widget.battle
        elif fromBattle == False: target = widget.hangar
        
        if hasattr(target, param) and getattr(target, param) != value:
          if fromBattle is not None and param in ['width', 'height', 'position', 'sniperPosition', 'artyPosition', 'strategicPosition'] and not target.isTouched:
            target.isTouched = True
            opposite = widget.hangar if fromBattle else widget.battle
            target.width = opposite.width
            target.height = opposite.height
            target.position = (opposite.position[0], opposite.position[1])
          
          setattr(target, param, value)
          self._isChanged = True
  
    if widget.positionMode == POSITION_MODE.SAME: update("position", position, False)
    update("url", url, None)
    update("flags", flags, None)
    update("positionMode", positionMode, None)
    update("layer", layer, None)
    update("width", width)
    update("height", height)
    update("position", position)
    update("sniperPosition", sniperPosition)
    update("artyPosition", artyPosition)
    update("strategicPosition", strategicPosition)
    update("isHidden", isHidden)
    update("isLocked", isLocked)
    update("isControlsAlwaysHidden", isControlsAlwaysHidden)
  
  def sendToTopPlan(self, wid):
    widget = self._widgetsByWid.get(wid, None)
    if widget is None: return
    
    maxOrder = max([w.order for w in self._widgets.values()])
    widget.order = maxOrder + 1
    
    self._isChanged = True
    

  def setWidgetWid(self, uuid, wid):
    widget = self._widgets.get(uuid, None)
    if widget is None: return

    if widget.wid is not None:
      del self._widgetsByWid[widget.wid]

    self._widgetsByWid[wid] = widget
    widget.wid = wid

  def getWidgetFlags(self, wid):
    widget = self._widgetsByWid.get(wid, None)
    if widget is None: return None

    return widget.flags

  def getPositionMode(self, wid):
    widget = self._widgetsByWid.get(wid, None)
    if widget is None: return None

    return widget.positionMode

  def _saveLoop(self):
    BigWorld.callback(1, self._saveLoop)

    if self._isChanged:
      self._save()

  def _save(self):
    self._isChanged = False
    
    data = json.dumps([w.toSerializable() for w in self._widgets.values()], indent=2)

    try:
      with open(ACTIVE_WIDGETS_PATH, "w") as f:
        f.write(data)
    except Exception as e:
      logger.error("Failed to save widget data: %s" % e)

  def _load(self):
    
    try:
      with open(ACTIVE_WIDGETS_PATH, "r") as f:
        data = json.load(f)
    except IOError as e:
      if e.errno == errno.ENOENT:
        logger.info("No widgets file found: %s" % e)
      else:
        logger.error("Failed to load widget data: %s" % e)
          
      return
    except Exception as e:
      logger.error("Failed to load widget data: %s" % e)
      return

    for w in data:
      try:
        widget = WidgetInfo.fromSerializable(w)
        self._widgets[widget.uuid] = widget
      except Exception as e:
        logger.error("Failed to load widget: %s" % e)

    logger.info("Loaded %d widgets" % len(self._widgets))
