
import Event

class EventsManager():
	
  def __init__(self):
    self.createWidget = Event.Event()
    self.changeUrl = Event.Event()

manager = EventsManager()