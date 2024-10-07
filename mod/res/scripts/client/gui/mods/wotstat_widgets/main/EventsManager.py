
import Event

class EventsManager():
	
  def __init__(self):
    self.createWidgetEvent = Event.Event()
    self.changeUrlEvent = Event.Event()
    
  def createWidget(self, url, width, height=-1):
    self.createWidgetEvent(url, width, height)
    
  def changeUrl(self, wid, url):
    self.changeUrlEvent(wid, url)

manager = EventsManager()