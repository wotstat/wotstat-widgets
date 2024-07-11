from functools import partial
import time
import sys
import socket
import struct
import threading
import io
from typing import Dict
import zlib
import queue
import signal
import os

from cefpython3 import cefpython as cef

TICK_DELTA = 0.01

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
  def OnLoadStart(self, browser, **_):
    log("[%s] Load started" % self.widget.url)
    browser.ExecuteJavascript(injectJs)

  # DisplayHandler
  def OnConsoleMessage(self, browser, level, message, **_):
    consoleLog(self.widget.url, level, message)

  # RenderHandler
  def GetViewRect(self, rect_out, *args, **kwargs):
    rect_out.extend([0, 0, self.widget.size[0], self.widget.size[1]])
    return True
  
  def OnPaint(self, browser, element_type, paint_buffer, width, height, **_):
    frameBuffer = paint_buffer.GetString(mode="rgba", origin="top-left")
    if width == self.widget.size[0] or height != self.widget.size[1]:
      pngBuffer = bufferToPng(frameBuffer, width, height)
      self.widget.sendFrame(width, height, pngBuffer)

    else:
      log("Invalid frame size: %s, %s" % (width, height), 'ERROR')

class Widget(object):
  def __init__(self, url, browser, width, height, sendFrame):
    self.url = url
    self.size = (width, height)
    self.browser = browser
    self.sendFrame = sendFrame

    bindings = cef.JavascriptBindings()
    bindings.SetFunction("onBodyResize", self.onBodyResize)
    browser.SetJavascriptBindings(bindings)

    self.handler = ClientHandler(self)
    browser.SetClientHandler(self.handler)

    browser.WasResized()

  def resize(self, width, height):
    self.size = (width, height)
    self.browser.WasResized()

  def reloadIgnoreCache(self):
    self.browser.ReloadIgnoreCache()

  def close(self):
    self.frameServer.close()
    self.browser.CloseBrowser(True)

  # JS Bindings
  def onBodyResize(self, height):
    self.resize(self.size[0], height)
    log("[%s] On resize: %s" % (self.url, height))

class CEFServer(object):
  def __init__(self, host='localhost', port=30000):
    self.host = host
    self.port = port
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.client_socket = None
    self.connected = False
    self.widgets = {} # type: Dict[int, Widget]

    log("CEF VERSION %s\n" % cef.__version__)   

    sys.excepthook = cef.ExceptHook
    settings = {
      "windowless_rendering_enabled": True,
      "background_color": 0x00,
    }
    
    switches = {
      "disable-gpu": "",
      "disable-gpu-compositing": "",
    }

    cef.Initialize(settings, switches)

  def startServer(self):
    self.socket.bind((self.host, self.port))
    self.socket.listen(1)
    log("Server listening on %s:%s" % (str(self.host), str(self.port)))
    self.client_socket, addr = self.socket.accept()
    if self.last_frame:
      self.client_socket.sendall(self.last_frame)
    log("Connection from %s" % str(addr))
    self.connected = True

  def stopServer(self):
    if self.client_socket:
      self.client_socket.close()
    self.socket.close()
    log("Server closed on %s:%s" % (str(self.host), str(self.port)))

  def sendFrame(self, uuid, width, height, frameBytes):
    uuidBytes = struct.pack('!I', uuid)
    widthBytes = struct.pack('!I', width)
    heightBytes = struct.pack('!I', height)
    frameLength = struct.pack('!I', len(frameBytes))

    frame = uuidBytes + widthBytes + heightBytes + frameLength + frameBytes
    if self.connected and self.client_socket:
      try:
        self.client_socket.sendall(frame)
      except Exception as e:
        log("Error sending frame: %s" % e, 'ERROR')
        self.connected = False

  def createWidget(self, uuid, url, width, height):
    log(f"Creating widget [{uuid}] with url: {url} and siz: {width}x{height}")

    browserSettings = {
      "windowless_frame_rate": 30,
    }

    windowInfo = cef.WindowInfo()
    windowInfo.SetAsOffscreen(0)

    browser = cef.CreateBrowserSync(window_info=windowInfo,
                                    settings=browserSettings,
                                    url=url)
    
    widget = Widget(url, browser, width, height, partial(self.sendFrame, uuid))
    self.widgets[uuid] = widget

  def resizeWidget(self, uuid, width, height):
    widget = self.widgets.get(uuid, None)
    if not widget: return

    if height == -1:
      aspect = widget.size[0] / widget.size[1]
      widget.resize(width, width / aspect)
    else:
      widget.resize(width, height)

  def reloadWidget(self, uuid):
    widget = self.widgets.get(uuid, None)
    if not widget: return

    widget.reloadIgnoreCache()

  def closeWidget(self, uuid):
    widget = self.widgets.get(uuid, None)
    if not widget: return

    widget.close()
    del self.widgets[uuid]

class Main(object):

  class Commands:
    OPEN_NEW_BROWSER = 'OPEN_NEW_BROWSER'
    RESIZE_BROWSER = 'RESIZE_BROWSER'
    RELOAD_BROWSER = 'RELOAD_BROWSER'
    CLOSE_BROWSER = 'CLOSE_BROWSER'

  killNow = False
  tasksQueue = queue.Queue()

  def __init__(self, port):

    signal.signal(signal.SIGINT, self.exitGracefully)
    signal.signal(signal.SIGTERM, self.exitGracefully)

    self.server = CEFServer(port=port)
    self.server.startServer()

    self.inputThread = threading.Thread(target=self.inputLoopThread)
    self.inputThread.start()

  def start(self):
    while self.inputThread.is_alive() and self.killNow == False:
      cef.MessageLoopWork()
      if not self.tasksQueue.empty():
        task, args = self.tasksQueue.get(timeout=TICK_DELTA)
        task(*args)
      else:
        time.sleep(TICK_DELTA)

    cef.Shutdown()
    log("Exiting")

  def inputLoopThread(self):
    while not self.killNow:
      line = sys.stdin.readline()
      if not line:
        log("EOF")
        break

      line = line.strip()
      self.tasksQueue.put((self.onCommand, (line,)))
    
  def onCommand(self, command: str):
    if command.startswith(Main.Commands.OPEN_NEW_BROWSER):
      parts = getCommandParts(command, 4)
      if not parts: return

      uuid, url, width, height = parts
      width = int(float(width))
      height = int(float(height))
      log(f"Opening widget [{uuid}], url: {url}, size: {width}x{height}")
      self.server.createWidget(uuid, url, width, height)
      return 
    
    if command.startswith(Main.Commands.RESIZE_BROWSER):
      parts = getCommandParts(command, 3)
      if not parts: return

      uuid, width, height = parts
      width = int(float(width))
      height = int(float(height))
      log(f"Resizing widget [{uuid}] to: {width}x{height}")
      self.server.resizeWidget(uuid, width, height)
      return
    
    if command.startswith(Main.Commands.RELOAD_BROWSER):
      parts = getCommandParts(command, 1)
      if not parts: return

      uuid = parts[0]
      log(f"Reloading widget [{uuid}]")
      self.server.reloadWidget(uuid)
      return
    
    if command.startswith(Main.Commands.CLOSE_BROWSER):
      parts = getCommandParts(command, 1)
      if not parts: return

      uuid = parts[0]
      log(f"Closing widget [{uuid}]")
      self.server.closeWidget(uuid)
    
    log(f"Unknown command: {command}")

  def exitGracefully(self, signum, frame):
    log("Exiting gracefully")
    self.killNow = True



if __name__ == '__main__':

  port = 30000
  if len(sys.argv) > 1:
    port = int(sys.argv[1])

  main = Main(port)
  main.start()





