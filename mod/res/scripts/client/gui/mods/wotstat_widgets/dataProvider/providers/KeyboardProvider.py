import BigWorld
from gui import InputHandler
import Keys

from ..DataProviderSDK import DataProviderSDK, State

from typing import Dict

class KeyboardProvider(object):
  
  states = {} # type: Dict[int, State]
  keycodeToName = {} # type: Dict[int, str]
  
  def __init__(self, sdk):
    # type: (DataProviderSDK) -> None
    
    InputHandler.g_instance.onKeyDown += self.__onKey
    InputHandler.g_instance.onKeyUp += self.__onKey
    
    
    for key in filter(lambda x: x.startswith('KEY_') or x.startswith('MODIFIER_'), vars(Keys).keys()):
      state = sdk.createState(['keyboard', key], False)
      self.states[Keys.__dict__[key]] = state
      self.keycodeToName[Keys.__dict__[key]] = key
      
    self.onAnyKey = sdk.createTrigger(['keyboard', 'onAnyKey'])
    
    
  def __onKey(self, event):
    # type: (BigWorld.KeyEvent) -> None
    if event.key in self.states:
      self.states[event.key].setValue(event.isKeyDown())
    
    if event.key in self.keycodeToName:
      key = self.keycodeToName[event.key]
      self.onAnyKey.trigger({'key': key, 'isKeyDown': event.isKeyDown()})
      