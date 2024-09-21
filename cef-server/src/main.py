from functools import partial
import math
import time
import sys
import socket
import struct
import threading
import base64
import io
from typing import Dict
import zlib
import queue
import signal
import os
from unpremultiply_rgba.unpremultiply_rgba import unpremultiply_rgba

from cefpython3 import cefpython as cef

TICK_DELTA = 0.01

os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

logLock = threading.Lock()
def log(msg, level='INFO'):
  with logLock:
    sys.stdout.write("[LOG][%s]%s\n" % (level, msg))
    sys.stdout.flush()

def consoleLog(url, level, msg):
  with logLock:
    namedLevel = ['0', 'DEBUG', 'INFO', 'WARNING', 'ERROR'][level] if level in range(5) else level
    sys.stdout.write("[CONSOLE][%s][%s]: %s\n" % (url, namedLevel, msg.encode("utf-8")))
    sys.stdout.flush()

with open(os.path.join(sys._MEIPASS, 'inject.js'), 'r') as f:
  injectJs = f.read()

def bufferToPng(buffer, width, height):
  def write_chunk(png_file, chunk_type, data):
    chunk_length = len(data)
    chunk = struct.pack("!I", chunk_length)
    chunk += chunk_type
    chunk += data
    crc = zlib.crc32(chunk_type)
    crc = zlib.crc32(data, crc)
    crc &= 0xffffffff
    crc = struct.pack("!I", crc)
    chunk += crc
    png_file.write(chunk)

  png_file = io.BytesIO()
  
  # PNG file signature
  png_file.write(b'\x89PNG\r\n\x1a\n')

  # IHDR chunk
  ihdr_data = struct.pack("!2I5B", width, height, 8, 6, 0, 0, 0)
  write_chunk(png_file, b'IHDR', ihdr_data)

  # IDAT chunk
  # Convert RGBA buffer to raw image data (scanlines with filter type 0)
  raw_data = b''.join(b'\x00' + buffer[y * width * 4:(y + 1) * width * 4] for y in range(height))
  compressed_data = zlib.compress(raw_data)
  write_chunk(png_file, b'IDAT', compressed_data)

  # IEND chunk
  write_chunk(png_file, b'IEND', b'')

  return png_file.getvalue()

def getCommandParts(command, count=4):
  parts = command.split(' ')
  if len(parts) != count+1:
    log(f"Invalid command: {command}")
    return None
  return parts[1:]

class ClientHandler(object):
  def __init__(self, widget):
    # type: (Widget) -> None
    self.widget = widget

  # LoadHandler
  def OnLoadingStateChange(self, browser, is_loading, **_):
    if not is_loading:
      log("[%s] Load finished" % self.widget.url)
      browser.ExecuteJavascript(injectJs)
      self.widget.setZoomPercent(self.widget.zoomLevel)
    else:
      log("[%s] Loading..." % self.widget.url)
    
  # DisplayHandler
  def OnConsoleMessage(self, browser, level, message, **_):
    consoleLog(self.widget.url, level, message)

  # RenderHandler
  def GetViewRect(self, rect_out, *args, **kwargs):
    rect_out.extend([0, 0, self.widget.size[0], self.widget.size[1]])
    return True
  
  def OnPaint(self, browser, element_type, paint_buffer, width, height, **_):
    if self.widget.suspensed:
      return
    
    frameBuffer = paint_buffer.GetString(mode="rgba", origin="top-left") # type: bytes
    if width == self.widget.size[0]:
      frameBuffer = bytearray(frameBuffer)
      frameBuffer = unpremultiply_rgba(frameBuffer)
      pngBuffer = bufferToPng(frameBuffer, width, height)
      self.widget.sendFrame(self.widget.getFlags(), width, height, pngBuffer)

    else:
      log("Invalid frame size: %s, %s" % (width, height), 'ERROR')

class Widget(object):

  class Flags:
    AUTO_HEIGHT = 1 << 0
    READY_TO_CLEAR_DATA = 1 << 1
  

  def __init__(self, url, browser, zoom, width, height, sendFrame):
    
    self.autoHeight = False
    self.readyToClearData = False
    self.lastBodyHeight = 0
    self.suspensed = False
    
    self.url = url
    self.size = (width, height)
    self.browser = browser
    self.sendFrame = sendFrame
    self.zoomLevel = zoom

    bindings = cef.JavascriptBindings()
    bindings.SetFunction("wotstatWidgetOnBodyResize", self.onBodyResize)
    bindings.SetFunction("wotstatWidgetOnFeatureFlagsChange", self.onFeatureFlagsChange)
    browser.SetJavascriptBindings(bindings)

    self.handler = ClientHandler(self)
    browser.SetClientHandler(self.handler)

    browser.WasResized()

  def resize(self, width, height):
    self.size = (width, height)

    if self.size[0] <= 0 or self.size[1] <= 0:
      log("Invalid size: %s, %s" % self.size, 'ERROR')
      if self.size[0] <= 0:
        self.size = (100, self.size[1])
      elif self.size[1] <= 0:
        self.size = (self.size[0], 100)
      else:
        self.size = (100, 100)

    self.browser.WasResized()

  def reloadIgnoreCache(self):
    self.browser.ReloadIgnoreCache()

  def showDevTools(self):
    self.browser.ShowDevTools()

  def close(self):
    self.browser.CloseBrowser(True)

  def setZoomPercent(self, zoom):
    self.zoomLevel = zoom
    self.browser.SetZoomLevel(math.log(zoom) / math.log(1.2))
    self.browser.WasResized()
    log("[%s] Zoom level set to: %s" % (self.url, zoom))

  def redraw(self):
    self.browser.Invalidate(cef.PET_VIEW)

  def resizeByHeight(self):
    if self.autoHeight and self.lastBodyHeight > 0:
      height = min(self.lastBodyHeight, 1000 * self.zoomLevel)
      self.resize(self.size[0], height)

  def getFlags(self):
    flags = 0

    if self.autoHeight: flags |= self.Flags.AUTO_HEIGHT
    if self.readyToClearData: flags |= self.Flags.READY_TO_CLEAR_DATA

    return flags
  
  def suspense(self):
    self.suspensed = True
  
  def resume(self):
    self.suspensed = False
  
  def sendWidgetCommand(self, command):
    self.browser.ExecuteJavascript("window.dispatchEvent(new CustomEvent('wotstat-widget-command', { detail: '%s' }))" % command)

  # JS Bindings
  def onBodyResize(self, height):
    self.lastBodyHeight = height
    self.resizeByHeight()

  def onFeatureFlagsChange(self, flags):
    autoHeight = flags.get('autoHeight', None)
    if autoHeight is not None: self.autoHeight = autoHeight
    
    readyToClearData = flags.get('readyToClearData', None)
    if readyToClearData is not None: self.readyToClearData = readyToClearData
    
    self.resizeByHeight()
    self.redraw()
    self.browser.WasResized()

class CEFServer(object):
  def __init__(self, host='localhost', port=30000, cachePath='', debug=False):
    self.host = host
    self.port = port
    self.debug = debug
    self.interfaceScale = 1.0
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.client_socket = None
    self.connected = False
    self.connectionThread = None
    self.widgets = {} # type: Dict[int, Widget]

    log("CEF VERSION %s\n" % cef.__version__)   

    sys.excepthook = cef.ExceptHook
    settings = {
      "windowless_rendering_enabled": True,
      "cache_path": cachePath,
    }
    
    switches = {
      "disable-gpu": "",
      "disable-gpu-compositing": "",
    }

    cef.Initialize(settings, switches)

  def startServer(self):
    self.socket.bind((self.host, self.port))
    self.socket.listen(1)
     
    def startThread():
      try:
        log("Server listening on %s:%s" % (str(self.host), str(self.port)))
        self.client_socket, addr = self.socket.accept()
        log("Connection from %s" % str(addr))
        self.connected = True
      except Exception as e:
        log('Terminating connection: %s' % e)
        self.connected = False

    self.connectionThread = threading.Thread(target=startThread)
    self.connectionThread.start()

  def stopServer(self):
    log("Stopping server")
    
    if self.client_socket:
      self.client_socket.close()
      
    self.socket.close()
    
    if self.connectionThread:
      self.connectionThread.join()
    
    log("Server closed on %s:%s" % (str(self.host), str(self.port)))

  def sendFrame(self, wid, flags, width, height, frameBytes):
    widBytes = struct.pack('!I', wid)
    flagsBytes = struct.pack('!I', flags)
    widthBytes = struct.pack('!I', width)
    heightBytes = struct.pack('!I', height)
    frameLength = struct.pack('!I', len(frameBytes))

    frame = widBytes + flagsBytes + widthBytes + heightBytes + frameLength + frameBytes
    if self.connected and self.client_socket:
      try:
        self.client_socket.sendall(frame)
      except Exception as e:
        log("Error sending frame: %s" % e, 'ERROR')
        self.connected = False

  def createWidget(self, wid, url, width, height):
    if height < 0:
      height = width

    log(f"Creating widget [{wid}] with url: {url} and size: {width}x{height}")

    browserSettings = {
      "windowless_frame_rate": 30,
    }

    windowInfo = cef.WindowInfo()
    windowInfo.SetAsOffscreen(0)

    browser = cef.CreateBrowserSync(window_info=windowInfo,
                                    settings=browserSettings,
                                    url=url)
    
    widget = Widget(url, browser, self.interfaceScale, width, height, partial(self.sendFrame, wid))
    self.widgets[wid] = widget

    if self.debug:
      widget.showDevTools()

  def resizeWidget(self, wid, width, height):
    widget = self.widgets.get(wid, None)
    if not widget: return

    if height < 0:
      aspect = widget.size[0] / widget.size[1]
      widget.resize(width, width / aspect)
    else:
      widget.resize(width, height)

  def reloadWidget(self, wid):
    widget = self.widgets.get(wid, None)
    if not widget: return

    widget.reloadIgnoreCache()

  def closeWidget(self, wid):
    widget = self.widgets.get(wid, None)
    if not widget: return

    widget.close()
    del self.widgets[wid]

  def setInterfaceScale(self, scale):
    self.interfaceScale = scale
    for widget in self.widgets.values():
      widget.setZoomPercent(scale)

  def redrawWidget(self, wid):
    widget = self.widgets.get(wid, None)
    if not widget: return

    widget.redraw()
    
  def suspendWidget(self, wid):
    widget = self.widgets.get(wid, None)
    if not widget: return

    widget.suspense()
    
  def resumeWidget(self, wid):
    widget = self.widgets.get(wid, None)
    if not widget: return

    widget.resume()
    
  def sendWidgetCommand(self, wid, command):
    widget = self.widgets.get(wid, None)
    if not widget: return

    widget.sendWidgetCommand(command)

class Commands:
  OPEN_NEW_WIDGET = 'OPEN_NEW_WIDGET'
  RESIZE_WIDGET = 'RESIZE_WIDGET'
  RELOAD_WIDGET = 'RELOAD_WIDGET'
  CLOSE_WIDGET = 'CLOSE_WIDGET'
  REDRAW_WIDGET = 'REDRAW_WIDGET'
  SET_INTERFACE_SCALE = 'SET_INTERFACE_SCALE'
  SUSPENSE_WIDGET = 'SUSPENSE_WIDGET'
  RESUME_WIDGET = 'RESUME_WIDGET'
  WIDGET_COMMAND = 'WIDGET_COMMAND'
  TERMINATE = 'TERMINATE'

class Main(object):
  killNow = threading.Event()
  tasksQueue = queue.Queue()

  def __init__(self, port, cachePath, debug):
    signal.signal(signal.SIGINT, self.exitGracefully)
    signal.signal(signal.SIGTERM, self.exitGracefully)

    self.inputThread = threading.Thread(target=self.inputLoopThread)
    self.inputThread.start()

    self.server = CEFServer(port=port, cachePath=cachePath, debug=debug)
    self.server.startServer()

  def start(self):
    while self.inputThread.is_alive() and not self.killNow.is_set():
      cef.MessageLoopWork()
      if not self.tasksQueue.empty():
        task, args = self.tasksQueue.get(timeout=TICK_DELTA)
        task(*args)
      else:
        time.sleep(TICK_DELTA)

    self.killNow.set()
    self.server.stopServer()
    self.inputThread.join()
    cef.Shutdown()
    log("Exiting")

  def inputLoopThread(self):
    while not self.killNow.is_set():
      line = sys.stdin.readline()
      if not line:
        log("EOF")
        break

      line = line.strip()
      if line == Commands.TERMINATE:
        self.killNow.set()
        break
      
      self.tasksQueue.put((self.onCommand, (line,)))
    
  def onCommand(self, command: str):
    if command.startswith(Commands.OPEN_NEW_WIDGET):
      parts = getCommandParts(command, 4)
      if not parts: return

      wid, url, width, height = parts
      wid = int(wid)
      width = int(float(width))
      height = int(float(height))
      log(f"Opening widget [{wid}], url: {url}, size: {width}x{height}")
      self.server.createWidget(wid, url, width, height)
      return 
    
    if command.startswith(Commands.RESIZE_WIDGET):
      parts = getCommandParts(command, 3)
      if not parts: return

      wid, width, height = parts
      wid = int(wid)
      width = int(float(width))
      height = int(float(height))
      log(f"Resizing widget [{wid}] to: {width}x{height}")
      self.server.resizeWidget(wid, width, height)
      return
    
    if command.startswith(Commands.RELOAD_WIDGET):
      parts = getCommandParts(command, 1)
      if not parts: return

      wid = int(parts[0])
      log(f"Reloading widget [{wid}]")
      self.server.reloadWidget(wid)
      return
    
    if command.startswith(Commands.CLOSE_WIDGET):
      parts = getCommandParts(command, 1)
      if not parts: return

      wid = int(parts[0])
      log(f"Closing widget [{wid}]")
      self.server.closeWidget(wid)
      return

    if command.startswith(Commands.SET_INTERFACE_SCALE):
      parts = getCommandParts(command, 1)
      if not parts: return

      scale = float(parts[0])
      log(f"Setting interface scale: {scale}")
      self.server.setInterfaceScale(scale)
      return
    
    if command.startswith(Commands.REDRAW_WIDGET):
      parts = getCommandParts(command, 1)
      if not parts: return

      wid = int(parts[0])
      log(f"Getting widget frame: {wid}")
      self.server.redrawWidget(wid)
      return
    
    if command.startswith(Commands.SUSPENSE_WIDGET):
      parts = getCommandParts(command, 1)
      if not parts: return

      wid = int(parts[0])
      log(f"Suspending widget: {wid}")
      self.server.suspendWidget(wid)
      return
    
    if command.startswith(Commands.RESUME_WIDGET):
      parts = getCommandParts(command, 1)
      if not parts: return

      wid = int(parts[0])
      log(f"Resuming widget: {wid}")
      self.server.resumeWidget(wid)
      return
    
    if command.startswith(Commands.WIDGET_COMMAND):
      parts = command.split(' ', 2)
      if len(parts) != 3:
        log(f"Invalid command: {command}")
        return

      _, wid, command = parts
      wid = int(wid)
      log(f"Sending widget command: {command} to {wid}")
      self.server.sendWidgetCommand(wid, command)
      return
    
    log(f"Unknown command: {command}")

  def exitGracefully(self, signum, frame):
    log("Exiting gracefully")
    self.killNow.set()


def parseArguments(argv):
  args = {}
  for arg in argv:
    if arg.startswith('--'):
      key_value = arg[2:].split('=', 1)
      if len(key_value) == 2:
        key, value = key_value
        args[key] = value
  return args

if __name__ == '__main__':
  arguments = parseArguments(sys.argv[1:])
  
  port = arguments.get('port', None)
  port = int(port) if port else int(input('Enter port: '))
  cachePath = arguments.get('cachePath', '')
  cachePathBase64 = arguments.get('cachePathBase64', None)
  devtools = bool(arguments.get('devtools', 'False') == 'True')
  
  if not cachePath and cachePathBase64:
    base64Bytes = cachePathBase64.encode('ascii')
    utf8Bytes = base64.b64decode(base64Bytes)
    cachePath = utf8Bytes.decode('utf-8')

  log(f"Starting CEF server on port {port}; cachePath: {cachePath}; devtools {devtools}")

  main = Main(port, cachePath, devtools)
  main.start()
  
  log("Close")





