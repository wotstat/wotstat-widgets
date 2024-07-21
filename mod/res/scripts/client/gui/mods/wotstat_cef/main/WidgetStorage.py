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
  uuid = ""
  wid = None
  url = ""
  width = 0
  height = 0
  x = 0
  y = 0
  isHidden = False
  isLocked = False
  flags = 0

  def toSerializable(self):
    return {
      "uuid": self.uuid,
      "url": self.url,
      "width": self.width,
      "height": self.height,
      "x": self.x,
      "y": self.y,
      "isHidden": self.isHidden,
      "isLocked": self.isLocked
    }
  
  @staticmethod
  def fromSerializable(data):
    w = WidgetInfo()

    w.uuid = data["uuid"]
    w.url = data["url"]
    w.width = data["width"]
    w.height = data["height"]
    w.x = data["x"]
    w.y = data["y"]
    w.isHidden = data["isHidden"]
    w.isLocked = data["isLocked"]

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
    widget.width = width
    widget.height = height
    widget.x = x
    widget.y = y
    widget.isHidden = isHidden
    widget.isLocked = isLocked
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
      
  def updateWidget(self, wid, url=None, width=None, height=None, x=None, y=None, isHidden=None, isLocked=None, flags=None):
    widget = self._widgetsByWid.get(wid, None)
    if widget is None: return

    def update(param, value):
      if param is not None and value is not None:
        if getattr(widget, param) != value:
          setattr(widget, param, value)
          self._isChanged = True
  
    update("url", url)
    update("width", width)
    update("height", height)
    update("x", x)
    update("y", y)
    update("isHidden", isHidden)
    update("isLocked", isLocked)
    update("flags", flags)

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
