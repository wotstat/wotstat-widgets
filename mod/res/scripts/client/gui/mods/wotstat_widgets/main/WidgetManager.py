from functools import partial
import json
import os
import errno

import BigWorld
from Singleton import Singleton
from uuid import uuid4
from typing import Dict, Callable

from aih_constants import CTRL_MODE_NAME  # noqa: F401

from ..common.Logger import Logger
from ..constants import ACTIVE_WIDGETS_PATH

from .CefServer import CefServer, server
from .WidgetStorage import WidgetInfo, POSITION_MODE, WidgetStorage


logger = Logger.instance()
storage = WidgetStorage.instance()

class WidgetState(object):
  
  def __init__(self, info, wid):
    # type: (WidgetInfo, str, int) -> None
    
    self.info = info
    self.wid = wid
    self.hasFirstFrame = False
    self.flags = 0
    self.insets = [0, 0, 0, 0]
    self.width = 0
    self.height = 0
  
  def setFrame(self, flags, insets, width, height):
    self.hasFirstFrame = True
    self.flags = flags
    self.insets = insets
    self.width = width
    self.height = height
    
  def hasFlags(self, flags):
    return self.flags is not None
    
  def isHangarOnly(self):
    return self.flags & CefServer.Flags.HANGAR_ONLY != 0
  
  def getPreferredPosition(self, battle, mode=None):
    # type: (bool, str) -> List[int]
    
    info = self.info
    
    hangarState = info.battle if not info.hangar.isTouched and info.battle.isTouched else info.hangar
    if not battle: return hangarState.position
    
    state = info.battle

    if not state.isTouched: return info.hangar.position
    
    if info.positionMode == POSITION_MODE.SAME: return hangarState.position
    if info.positionMode == POSITION_MODE.HANGAR_BATTLE: return state.position
    
    if mode == CTRL_MODE_NAME.SNIPER: return state.sniperPosition or state.position
    if mode == CTRL_MODE_NAME.ARTY: return state.artyPosition or state.strategicPosition or state.position
    if mode == CTRL_MODE_NAME.STRATEGIC: return state.strategicPosition or state.artyPosition or state.position
    
    return state.position
  
  def getPreferredSize(self, battle, mode=None):
    # type: (bool, str) -> List[int]
    
    info = self.info
    
    hangarState = info.battle if not info.hangar.isTouched and info.battle.isTouched else info.hangar
    if not battle: return hangarState.size
    
    state = info.battle

    if not state.isTouched: return info.hangar.size
    
    if info.sizeMode == POSITION_MODE.SAME: return hangarState.size
    if info.sizeMode == POSITION_MODE.HANGAR_BATTLE: return state.size
    
    if mode == CTRL_MODE_NAME.SNIPER: return state.sniperSize or state.size
    if mode == CTRL_MODE_NAME.ARTY: return state.artySize or state.strategicSize or state.size
    if mode == CTRL_MODE_NAME.STRATEGIC: return state.strategicSize or state.artySize or state.size
    
    return state.size

class WidgetManager(Singleton):
  
  _widgetsByWid = {} # type: Dict[str, WidgetState]
  _widgetsByUUID = {} # type: Dict[str, WidgetState]
  _isReady = False
  _lastWid = 0

  @staticmethod
  def instance():
    return WidgetManager()
  
  def _singleton_init(self):
    pass
  
  def setup(self):
    if server.isReady: self._onServerReady()
    else: server.onSetupComplete += self._onServerReady
  
  def createWidget(self, url, width, height=-1):
    self._lastWid += 1
    wid = self._lastWid
    info = storage.createWidget(url, width, height)
    state = WidgetState(info, wid)
    self._widgetsByWid[wid] = state
    self._widgetsByUUID[info.uuid] = state
    
  def removeWidget(self, wid):
    state = self._widgetsByWid.pop(wid)
    if state is not None: return
    
    self._widgetsByUUID.pop(state.info.uuid)
    storage.removeWidget(state.info.uuid)
    server.closeWidget(wid)
  
  def changeUrl(self, wid, url):
    server.changeWidgetUrl(wid, url)
  
  def getWidget(self, uuid):
    # type: (str) -> WidgetState
    if uuid in self._widgetsByUUID: return self._widgetsByUUID[uuid]
    return None
  
  def _onServerReady(self):
    
    server.onFrame += self._onFrame
    
    for widget in storage.getAllWidgets():
      self._lastWid += 1
      wid = self._lastWid
      
      state = WidgetState(widget, wid)
      self._widgetsByWid[wid] = state
      self._widgetsByUUID[widget.uuid] = state
      
      server.createNewWidget(wid, widget.url, 10, 10)
      
  def _onFrame(self, wid, flags, insets, width, height, length, data):
    state = self._widgetsByWid.get(wid, None)
    if state is None: return
    
    if state.hasFirstFrame:
      state.setFrame(flags, insets, width, height)
    else:
      state.setFrame(flags, insets, width, height)
    
  