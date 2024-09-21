import os
import BigWorld

import subprocess
import threading
import socket
import struct
from Queue import Queue
from typing import Tuple
import base64

from Event import Event
from external_strings_utils import unicode_from_utf8
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore

from ..common.utils import isPortAvailable
from ..common.ExceptionHandling import withExceptionHandling
from ..common.Logger import Logger
from ..constants import CEF_EXE_PATH

logger = Logger.instance()

_preferences_path = unicode_from_utf8(BigWorld.wg_getPreferencesFilePath())[1]
CACHE_PATH = os.path.normpath(os.path.join(os.path.dirname(_preferences_path), 'mods', 'wotstat.widgets', 'webcache'))
CACHE_PATH_BASE64 = base64.b64encode(CACHE_PATH.encode('utf-8')).decode('ascii')

logger = Logger.instance()

@withExceptionHandling()
def setup():
  if not os.path.isdir(CACHE_PATH):
    os.makedirs(CACHE_PATH)
    
setup()


class Commands:
  OPEN_NEW_WIDGET = 'OPEN_NEW_WIDGET'
  RESIZE_WIDGET = 'RESIZE_WIDGET'
  RELOAD_WIDGET = 'RELOAD_WIDGET'
  CLOSE_WIDGET = 'CLOSE_WIDGET'
  SET_INTERFACE_SCALE = 'SET_INTERFACE_SCALE'
  REDRAW_WIDGET = 'REDRAW_WIDGET'
  SUSPENSE_WIDGET = 'SUSPENSE_WIDGET'
  RESUME_WIDGET = 'RESUME_WIDGET'
  TERMINATE = 'TERMINATE'
  WIDGET_COMMAND = 'WIDGET_COMMAND'


class CefServer(object):

  class Flags:
    AUTO_HEIGHT = 1 << 0
    READY_TO_CLEAR_DATA = 1 << 1

  killNow = threading.Event()
  socket = None
  queue = Queue()
  onFrame = Event()
  isReady = False
  onSetupComplete = Event()
  hasProcessError = False
  onProcessError = Event()
  settingsCore = dependency.descriptor(ISettingsCore) # type: ISettingsCore

  def __init__(self):
    self._checkQueueLoop()
    self.receiverThread = None
    self.outputThread = None
    self.errorOutputThread = None
    self.killNow.set()
    self.process = None

  @withExceptionHandling()
  def enable(self, devtools=False):
    self.killNow.clear()

    try:
      self._startServer(devtools)
    except Exception as e:
      logger.critical("Error starting CEF server: %s" % e)
      if self.process and self.process.poll() is None:
        self.process.terminate()
      self.killNow.set()
      self.hasProcessError = True
      self.onProcessError(str(e))
      
  def _startServer(self, devtools):
    port = 33100
    for _ in range(100):
      if isPortAvailable(port): break
      port += 1

    startupInfo = subprocess.STARTUPINFO()
    if not devtools:
      startupInfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
      startupInfo.wShowWindow = subprocess.SW_HIDE
      
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUTF8'] = '1'
    env['PYTHONLEGACYWINDOWSSTDIO'] = '1'
    
    self.process = subprocess.Popen([
        CEF_EXE_PATH,
        '--port=' + str(port),
        '--devtools=' + str(devtools),
        '--cachePathBase64=' + CACHE_PATH_BASE64,
      ],
      startupinfo=startupInfo,
      env=env,
      stdin=subprocess.PIPE,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE)
    
    self.outputThread = threading.Thread(target=self._readOutputLoop)
    self.outputThread.start()

    self.errorOutputThread = threading.Thread(target=self._readErrorOutputLoop)
    self.errorOutputThread.start()

    logger.info("CEF server started")

    logger.info("Waiting for a connection on port: %s..." % str(port))
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.connect(('127.0.0.1', port))
    logger.info("Connected")

    self.receiverThread = threading.Thread(target=self._socketReceiverLoop, args=(self.socket, self.queue))
    self.receiverThread.start()

    self.settingsCore.interfaceScale.onScaleChanged += self._setInterfaceScale
    self.isReady = True
    self._setInterfaceScale()
    self.onSetupComplete()
    

  @withExceptionHandling()
  def dispose(self):
    if self.killNow.is_set(): return
    logger.info("CEF server stopping")
    
    self.isReady = False
    try: self._wrightInput(Commands.TERMINATE)
    except Exception as e: pass
    self.killNow.set()
    
    if self.outputThread: self.outputThread.join()
    if self.receiverThread: self.receiverThread.join()
    if self.errorOutputThread: self.errorOutputThread.join()
    
    if self.process.poll() is None:
      try:
        self.process.wait(1)
      except Exception as e:
        self.process.terminate()
    
    logger.info("CEF server stopped")

  def createNewWidget(self, wid, url, width, height):
    self._sendCommand(Commands.OPEN_NEW_WIDGET, wid, url, width, height)

  def resizeWidget(self, wid, width, height):
    logger.debug("Resize widget: %s to %sx%s" % (wid, width, height))
    self._sendCommand(Commands.RESIZE_WIDGET, wid, width, height)

  def reloadWidget(self, wid):
    logger.debug("Reload widget: %s" % wid)
    self._sendCommand(Commands.RELOAD_WIDGET, wid)

  def closeWidget(self, wid):
    logger.debug("Close widget: %s" % wid)
    self._sendCommand(Commands.CLOSE_WIDGET, wid)

  def redrawWidget(self, wid):
    logger.debug("Redraw widget: %s" % wid)
    self._sendCommand(Commands.REDRAW_WIDGET, wid)
    
  def suspenseWidget(self, wid):
    logger.debug("Suspense widget: %s" % wid)
    self._sendCommand(Commands.SUSPENSE_WIDGET, wid)
    
  def resumeWidget(self, wid):
    logger.debug("Resume widget: %s" % wid)
    self._sendCommand(Commands.RESUME_WIDGET, wid)
    
  def sendWidgetCommand(self, wid, command):
    logger.debug("Send widget command: %s" % command)
    self._sendCommand(Commands.WIDGET_COMMAND, wid, command)

  def _setInterfaceScale(self, scale=None):
    if scale is None:
      scale = self.settingsCore.interfaceScale.get()
    logger.info("Set interface scale: %s" % scale)
    self._sendCommand(Commands.SET_INTERFACE_SCALE, scale)

  def _readErrorOutputLoop(self):
    while not self.killNow.is_set():
      if not self.process: continue

      output = self.process.stderr.readline()
      if output == '' and self.process.poll() is not None: continue

      if not output: continue

      line = output.decode('utf-8', errors='replace').strip()
      if not line: continue

      if line.startswith('DevTools listening on'):
        logger.info(line)
        continue
      
      logger.error(line)

    logger.info("Error output loop stopped")

  def _readOutputLoop(self):
    while not self.killNow.is_set():
      if not self.process: continue

      output = self.process.stdout.readline()
      if output == '' and self.process.poll() is not None: continue

      if not output: continue

      line = output.decode('utf-8', errors='replace').strip()
      if not line: continue

      if line.startswith('[LOG]'):
        line = line[5:]
        if line.endswith('\n'):
          line = line[:-1]
        template = '[SERVER] %s'
        if line.startswith('[DEBUG]'):
          logger.debug(template % line[7:])
        elif line.startswith('[INFO]'):
          logger.info(template % line[6:])
        elif line.startswith('[WARN]'):
          logger.warn(template % line[6:])
        elif line.startswith('[ERROR]'):
          logger.error(template % line[7:])
        else:
          logger.error('Unknown level: %s' % line)
      elif line.startswith('[CONSOLE]'):
        logger.info(line)
      else:
        logger.error('Unknown format: %s' % line)

    logger.info("Output loop stopped")

  def _wrightInput(self, inputData):
    try:
      logger.debug("Send input data: %s" % str(inputData))
      self.process.stdin.write(str(inputData) + '\n')
      self.process.stdin.flush()
    except Exception as e:
      logger.error("Error writing input: %s" % e)
      if not self.killNow.is_set():
        self.isReady = False
        self.killNow.set()
        self.hasProcessError = True
        self.onProcessError(str(e))

  @withExceptionHandling()
  def _sendCommand(self, command, *args):
    if self.killNow.is_set(): return
    cmd = command + ' ' + ' '.join([str(arg) for arg in args])
    self._wrightInput(str(cmd))

  def _readFrame(self, sock):
    # type: (socket.socket) -> Tuple[int, int, int, bytes]

    wid_bytes = sock.recv(4)
    if not wid_bytes: return None

    flags_bytes = sock.recv(4)
    if not flags_bytes: return None

    width_bytes = sock.recv(4)
    if not width_bytes: return None
    
    height_bytes = sock.recv(4)
    if not height_bytes: return None
    
    length_bytes = sock.recv(4)
    if not length_bytes: return None
    
    wid = struct.unpack('!I', wid_bytes)[0]
    flags = struct.unpack('!I', flags_bytes)[0]
    width = struct.unpack('!I', width_bytes)[0]
    height = struct.unpack('!I', height_bytes)[0]
    length = struct.unpack('!I', length_bytes)[0]


    READ_SIZE = 4096
    read = 0
    data = b''
    while read < length:
      temp = sock.recv(min(READ_SIZE, length - read))
      if not temp: return None
      read += len(temp)
      data += temp
    
    if not data: return None

    return wid, flags, width, height, length, data

  def _socketReceiverLoop(self, sock, queue):
    # type: (socket.socket, Queue) -> None
    while not self.killNow.is_set():
      try:
        frame = self._readFrame(sock)
        if frame is None:
          logger.info("Disconnected from server.")
          break
        
        queue.put(frame)
      except Exception as e:
        if not self.killNow.is_set(): logger.error("Error reading frame: %s" % e)
        break

  def _checkQueueLoop(self):
    # TODO: Sync to FPS
    BigWorld.callback(1/120, self._checkQueueLoop)

    newFrames = {}

    while not self.queue.empty():
      wid, flags, width, height, length, data = self.queue.get()
      newFrames[wid] = (flags, width, height, length, data)
      
    for wid, frame in newFrames.items():
      flags, width, height, length, data = frame
      if data:
        self.onFrame(wid, flags, width, height, length, data)


server = CefServer()