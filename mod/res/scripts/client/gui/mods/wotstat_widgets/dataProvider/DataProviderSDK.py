import json
from typing import List

from .WebSocketDataProvider import WebSocketDataProvider, WSClient
from .ILogger import ILogger

def canSerializeValue(value):
  try:
    str = json.dumps(value)
    return True
  except Exception as e:
    return e

class State(object):
  def __init__(self, path, wsDataProvider, initialValue = None):
    # type: (List[str], WebSocketDataProvider, any) -> None
    self.__path = path
    self.__wsDataProvider = wsDataProvider
    self.__value = initialValue
    
  def getValue(self):
    return self.__value
  
  def setValue(self, value):
    e = canSerializeValue(value)
    if e != True:
      raise Exception("Failed to serialize value: %s" % e)
    
    self.__value = value
    path, value = self.getPathValue()
    self.__wsDataProvider.sendMessage(json.dumps({ "type": "state", "path": path, "value": value }))
    
  def getPathValue(self):
    return ('.'.join(self.__path), self.__value)
  
class Trigger(object):
  def __init__(self, path, wsDataProvider):
    # type: (List[str], WebSocketDataProvider) -> None
    self.__path = path
    self.__wsDataProvider = wsDataProvider
    
  def trigger(self, value=None):
    e = canSerializeValue(value)
    if e != True:
      raise Exception("Failed to serialize value: %s" % e)
    
    self.__wsDataProvider.sendMessage(json.dumps({ "type": "trigger", "path": '.'.join(self.__path), "value": value }))

class DPExtension(object):
  def __init__(self, name, sdk):
    # type: (str, DataProviderSDK) -> None
    self.__sdk = sdk
    self.__name = name
    
  def createState(self, path, initialValue = None):
    # type: (List[str] | str, any) -> State
    return self.__sdk.createState(['extensions', self.__name] + path, initialValue)
  
  def createTrigger(self, path):
    # type: (List[str] | str) -> Trigger
    return self.__sdk.createTrigger(['extensions', self.__name] + path)

class DataProviderSDK(object):
  
  def __init__(self, wsDataProvider, logger):
    # type: (WebSocketDataProvider, ILogger) -> None
    self.wsDataProvider = wsDataProvider
    self.logger = logger
    self.states = [] # type: List[State]
    self.extensionsState = self.createState('registeredExtensions', [])
    wsDataProvider.onClientConnected += self.__onClientConnected
    
  def createState(self, path, initialValue = None):
    # type: (List[str] | str, any) -> State
    if isinstance(path, str):
      path = [path]
    
    state = State(path, self.wsDataProvider, initialValue)
    self.states.append(state)
    self.logger.debug("State created: %s" % str(path))
    
    return state
  
  def createTrigger(self, path):
    # type: (List[str] | str) -> Trigger
    if isinstance(path, str):
      path = [path]
    
    trigger = Trigger(path, self.wsDataProvider)
    self.logger.debug("Trigger created: %s" % str(path))
    
    return trigger
  
  def registerExtension(self, extension):
    # type: (str) -> DPExtension
    if extension in self.extensionsState.getValue():
      raise Exception("Extension already registered: %s" % extension)
    
    self.extensionsState.setValue(self.extensionsState.getValue() + [extension])
    return DPExtension(extension, self)
  
  def setup(self):
    self.wsDataProvider.setup()
  
  def dispose(self):
    self.wsDataProvider.dispose()
    self.logger.info("DataProviderSDK disposed")
    
  def __onClientConnected(self, client):
    # type: (WSClient) -> None
    
    client.send_message_text(json.dumps({
      "type": "init",
      "states": [ { "path": t[0], "value": t[1] } for t in [state.getPathValue() for state in self.states]] 
    }))
    
    self.logger.info("Sent all states to new client")
