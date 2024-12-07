
from .WidgetStorage import LAYER, POSITION_MODE

class MainViewMeta(object):
  
  def _as_onFrame(self, wid, width, height, data, shift):
    self.flashObject.as_onFrame(wid, width, height, data, shift)