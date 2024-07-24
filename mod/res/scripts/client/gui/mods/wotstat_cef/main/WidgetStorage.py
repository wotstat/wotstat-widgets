import json
import os

import BigWorld
from Singleton import Singleton
from uuid import uuid4
from typing import Dict  # noqa: F401

from ..common.Logger import Logger
from ..constants import ACTIVE_WIDGETS_PATH

def setup():
  dir = os.path.dirname(ACTIVE_WIDGETS_PATH)
  if not os.path.isdir(dir):
    os.makedirs(dir)

setup()

class WidgetInfo(object):
  
  class PositionState(object):
    def __init__(self):
      self.width = 0
      self.height = 0
      self.x = 0
      self.y = 0
      self.isHidden = False
      self.isLocked = False
    
  def __init__(self):
    self.uuid = ""
    self.wid = None
    self.url = ""
    self.hangar = WidgetInfo.PositionState()
    self.battle = WidgetInfo.PositionState()
    self.flags = 0

  def toSerializable(self):
    return {
      "uuid": self.uuid,
      "url": self.url,
      "hangar": {
        "width": self.hangar.width,
        "height": self.hangar.height,
        "x": self.hangar.x,
        "y": self.hangar.y,
        "isHidden": self.hangar.isHidden,
        "isLocked": self.hangar.isLocked
      },
      "battle": {
        "width": self.battle.width,
        "height": self.battle.height,
        "x": self.battle.x,
        "y": self.battle.y,
        "isHidden": self.battle.isHidden,
        "isLocked": self.battle.isLocked
      },
    }
  
  @staticmethod
  def fromSerializable(data):
    w = WidgetInfo()

    w.uuid = data["uuid"]
    w.url = data["url"]
    
    hangar = data.get("hangar", {})
    w.hangar.width = hangar.get("width", 0)
    w.hangar.height = hangar.get("height", 0)
    w.hangar.x = hangar.get("x", 0)
    w.hangar.y = hangar.get("y", 0)
    w.hangar.isHidden = hangar.get("isHidden", False)
    w.hangar.isLocked = hangar.get("isLocked", False)
    
    battle = data.get("battle", {})
    w.battle.width = battle.get("width", 0)
    w.battle.height = battle.get("height", 0)
    w.battle.x = battle.get("x", 0)
    w.battle.y = battle.get("y", 0)
    w.battle.isHidden = battle.get("isHidden", False)
    w.battle.isLocked = battle.get("isLocked", False)
    
    return w

logger = Logger.instance()

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
    return self._widgets.values()
  
  def addWidget(self, wid, url, width=100, height=100, x=-1, y=-1, isHidden=False, isLocked=False):
    uuid = str(uuid4())
    
    widget = WidgetInfo()
    widget.uuid = uuid
    widget.wid = wid
    widget.url = url
    
    widget.battle.width = width
    widget.battle.height = height
    widget.battle.x = x
    widget.battle.y = y
    widget.battle.isHidden = isHidden
    widget.battle.isLocked = isLocked
    
    widget.hangar.width = width
    widget.hangar.height = height
    widget.hangar.x = x
    widget.hangar.y = y
    widget.hangar.isHidden = isHidden
    widget.hangar.isLocked = isLocked
    
    self._widgets[uuid] = widget
    self._widgetsByWid[wid] = widget

    self._isChanged = True


  def removeWidget(self, wid):
    for key, widget in self._widgets.items():
      if widget.wid == wid:
        del self._widgets[key]
        break

    del self._widgetsByWid[wid]

    self._isChanged = True
      
  def updateWidget(self, wid, fromBattle, url=None, width=None, height=None, x=None, y=None, isHidden=None, isLocked=None, flags=None):
    widget = self._widgetsByWid.get(wid, None)
    if widget is None: return

    def update(param, value, fromBattle=fromBattle):
      if param is not None and value is not None:
        target = widget

        if fromBattle == True: target = widget.battle
        elif fromBattle == False: target = widget.hangar
        
        if getattr(target, param) != value:
          setattr(target, param, value)
          self._isChanged = True
  
    update("url", url, None)
    update("flags", flags, None)
    
    update("width", width)
    update("height", height)
    update("x", x)
    update("y", y)
    update("isHidden", isHidden)
    update("isLocked", isLocked)

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
