from functools import partial
import time
import sys
import socket
import struct
import threading
import io
import zlib
import queue
import signal
import os

from cefpython3 import cefpython as cef


class Commands:
  OPEN_NEW_BROWSER = 'OPEN_NEW_BROWSER'
  RESIZE_BROWSER = 'RESIZE_BROWSER'

killNow = False
logLock = threading.Lock()
def log(msg, level='INFO'):
  with logLock:
    sys.stdout.write("[LOG][%s]%s\n" % (level, msg))
    sys.stdout.flush()

def consoleLog(url, level, msg):
  with logLock:
    namedLevel = ['0', 'DEBUG', 'INFO', 'WARNING', 'ERROR'][level] if level in range(5) else level
    sys.stdout.write("[CONSOLE][%s][%s]: %s\n" % (url, namedLevel, msg))
    sys.stdout.flush()

log("CEF VERSION %s\n" % cef.__version__)

with open(os.path.join(sys._MEIPASS, 'inject.js'), 'r') as f:
  injectJs = f.read()

widgetsByPort = {}

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

class FrameServer:
  def __init__(self, host='localhost', port=30001):
    self.host = host
    self.port = port
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.client_socket = None
    self.connected = False
    self.last_frame = None

  def startServer(self):
    self.socket.bind((self.host, self.port))
    self.socket.listen(1)
    log("Server listening on %s:%s" % (str(self.host), str(self.port)))
    self.client_socket, addr = self.socket.accept()
    if self.last_frame:
      self.client_socket.sendall(self.last_frame)
    log("Connection from %s" % str(addr))
    self.connected = True

  def sendFrame(self, width, height, frame_bytes):
    widthBytes = struct.pack('!I', width)
    heightBytes = struct.pack('!I', height)
    frameLength = struct.pack('!I', len(frame_bytes))

    self.last_frame = widthBytes + heightBytes + frameLength + frame_bytes
    if self.connected and self.client_socket:
      try:
        self.client_socket.sendall(self.last_frame)
      except Exception as e:
        log("Error sending frame: %s" % e, 'ERROR')
        self.connected = False

  def close(self):
    if self.client_socket:
      self.client_socket.close()
    self.socket.close()
    log("Server closed on %s:%s" % (str(self.host), str(self.port)))

class ClientHandler(object):
  def __init__(self, widget):
    # type: (WidgetHandler) -> None
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
      pngBytes = bufferToPng(frameBuffer, width, height)
      self.widget.frameServer.sendFrame(width, height, pngBytes)
    else:
      log("Invalid frame size: %s, %s" % (width, height), 'ERROR')

class WidgetHandler(object):
  def __init__(self, url, browser, port, width):
    self.url = url
    self.size = (width, 100)
    self.browser = browser

    bindings = cef.JavascriptBindings()
    bindings.SetFunction("onBodyResize", self.onBodyResize)
    browser.SetJavascriptBindings(bindings)

    self.frameServer = FrameServer(port=port)
    frameServerThread = threading.Thread(target=self.frameServer.startServer)
    frameServerThread.start()

    self.handler = ClientHandler(self)
    browser.SetClientHandler(self.handler)

    browser.WasResized()

  def resize(self, width, height):
    self.size = (width, height)
    self.browser.WasResized()

  # JS Bindings
  def onBodyResize(self, height):
    self.resize(self.size[0], height)
    log("[%s] On resize: %s" % (self.url, height))


def createBrowser(url, port, width):
  browserSettings = {
    "windowless_frame_rate": 30,
  }

  windowInfo = cef.WindowInfo()
  windowInfo.SetAsOffscreen(0)

  browser = cef.CreateBrowserSync(window_info=windowInfo,
                                  settings=browserSettings,
                                  url=url)
  

  widget = WidgetHandler(url, browser, port, width)
  widgetsByPort[port] = widget

  return browser, widget

def resizeBrowser(port, width):
  widget = widgetsByPort.get(port, None) # type: WidgetHandler
  if widget:
    widget.resize(width, widget.size[1])
  else:
    log(f"Widget not found for port: {port}", 'ERROR')

tasksQueue = queue.Queue()

def onCommand(command):
  # type: (str) -> None

  if command.startswith(Commands.OPEN_NEW_BROWSER):
    parts = command.split(' ')
    if len(parts) != 4:
      log(f"Invalid command: {command}")
      return

    url, port, width = parts[1:]
    port = int(port)
    width = int(float(width))
    log(f"Opening browser with url: {url} on port: {port}")
    createBrowser(url, port, width)
    return 
  
  if command.startswith(Commands.RESIZE_BROWSER):
    parts = command.split(' ')
    if len(parts) != 3:
      log(f"Invalid command: {command}")
      return

    port, width = parts[1:]
    port = int(port)
    width = int(float(width))
    log(f"Resizing browser on port: {port} to width: {width}")
    resizeBrowser(port, width)
    return 
  

  log(f"Unknown command: {command}")

def inputLoop():
  while not killNow:
    line = sys.stdin.readline()
    if not line:
      log("EOF")
      break

    line = line.strip()
    tasksQueue.put((onCommand, (line,)))

def exitGracefully(signum, frame):
  log("Exiting gracefully")
  global killNow
  killNow = True

def main():
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

  inputThread = threading.Thread(target=inputLoop)
  inputThread.start()

  signal.signal(signal.SIGINT, exitGracefully)
  signal.signal(signal.SIGTERM, exitGracefully)

  while inputThread.is_alive() and killNow == False:
    cef.MessageLoopWork()
    try:
      if not tasksQueue.empty():
        task, args = tasksQueue.get(timeout=0.01)
        task(*args)
      else:
        time.sleep(0.01)
    except queue.Empty:
      pass

  cef.Shutdown()
  log("Exiting")
  
if __name__ == '__main__':
  main()





