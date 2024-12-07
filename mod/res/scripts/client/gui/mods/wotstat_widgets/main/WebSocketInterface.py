import time
import BigWorld

from threading import Thread

from ..common.simple_websocket_server import WebSocket, WebSocketServer
from ..common.ExceptionHandling import withExceptionHandling
from ..common.Logger import Logger
from .WidgetManager import WidgetManager

logger = Logger.instance()
manager = WidgetManager.instance()

enabled = True
lastAddTime = 0

class WSClient(WebSocket):
  @withExceptionHandling()
  def handle(self):
    global lastAddTime
    
    logger.debug("Received message: %s" % str(self.data))
    if self.data == "ping":
      self.send_message_text("pong")
      
    if self.data.startswith('ADD_WIDGET'):
      if BigWorld.time() - lastAddTime < 1: return
      lastAddTime = BigWorld.time()
      
      parts = self.data.split(' ')
      if len(parts) != 2: return
      
      url = parts[1]
      manager.createWidget(url, 300, -1)
    
  @withExceptionHandling()
  def connected(self):
    logger.info("Connected %s" % str(self.address))
     
class WebSocketInterface(object):
  def __init__(self):
    self.server = None
    self.serverThread = None
      
  def setup(self):    
    self.server = WebSocketServer('', 38201, WSClient)
    
    self.serverThread = Thread(target=self._requestLoop, args=(self.server,))
    self.serverThread.start()
    
    logger.info("WebSocketInterface started")
      
  def _requestLoop(self, server):
    # type: (WebSocketServer) -> None
    while enabled:
      try:
        server.handle_request()
      except Exception as e:
        logger.error("Error in requestLoop: %s" % e)
        time.sleep(0.1)
          
  def dispose(self):
    # type: () -> None
    global enabled
    enabled = False
    
    logger.info("WebSocketInterface stopping")
    
    if self.server is not None:
      self.server.close()
      self.server = None
      
    if self.serverThread is not None:
      self.serverThread.join()
    
    logger.info("WebSocketInterface stopped")
