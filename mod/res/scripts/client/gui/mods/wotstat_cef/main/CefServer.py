import BigWorld

import subprocess
import threading
import socket
import struct
from Queue import Queue
from typing import Tuple

from Event import Event
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore

from ..common.utils import isPortAvailable
from ..common.Logger import Logger
from ..constants import CEF_EXE_PATH

logger = Logger.instance()

class Commands:
  OPEN_NEW_WIDGET = 'OPEN_NEW_WIDGET'
  RESIZE_WIDGET = 'RESIZE_WIDGET'
  RELOAD_WIDGET = 'RELOAD_WIDGET'
  CLOSE_WIDGET = 'CLOSE_WIDGET'
  SET_INTERFACE_SCALE = 'SET_INTERFACE_SCALE'
  REDRAW_WIDGET = 'REDRAW_WIDGET'


class CefServer(object):

  class Flags:
    AUTO_HEIGHT = 1 << 0

  enabled = False
  socket = None
  queue = Queue()
  onFrame = Event()
  settingsCore = dependency.descriptor(ISettingsCore) # type: ISettingsCore

  def __init__(self):
    self._checkQueueLoop()

  def enable(self, devtools=False):
    self.enabled = True

    port = 33100
    for _ in range(100):
      if isPortAvailable(port): break
      port += 1

    startupInfo = subprocess.STARTUPINFO()
    if not devtools:
      startupInfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
      startupInfo.wShowWindow = subprocess.SW_HIDE

    self.process = subprocess.Popen([CEF_EXE_PATH, str(port), str(devtools)],
      startupinfo=startupInfo,
      stdin=subprocess.PIPE,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE)
    
    outputThread = threading.Thread(target=self._readOutputLoop)
    outputThread.start()

    errorOutputThread = threading.Thread(target=self._readErrorOutputLoop)
    errorOutputThread.start()

    logger.info("CEF server started")

    logger.info("Waiting for a connection on port: %s..." % str(port))
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.connect(('127.0.0.1', port))
    logger.info("Connected")

    receiver_thread = threading.Thread(target=self._socketReceiverLoop, args=(self.socket, self.queue))
    receiver_thread.daemon = True
    receiver_thread.start()

    self.settingsCore.interfaceScale.onScaleChanged += self._setInterfaceScale
    self._setInterfaceScale()

  def dispose(self):
    self.enabled = False
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

  def _setInterfaceScale(self, scale=None):
    if scale is None:
      scale = self.settingsCore.interfaceScale.get()
    logger.info("Set interface scale: %s" % scale)
    self._sendCommand(Commands.SET_INTERFACE_SCALE, scale)

  def _readErrorOutputLoop(self):
    while self.enabled:
      if not self.process: continue

      output = self.process.stderr.readline()
      if output == '' and self.process.poll() is not None: continue

      if not output: continue

      line = output.decode().strip()
      if not line: continue

      logger.error(line)

    logger.info("Error output loop stopped")

  def _readOutputLoop(self):
    while self.enabled:
      if not self.process: continue

      output = self.process.stdout.readline()
      if output == '' and self.process.poll() is not None: continue

      if not output: continue

      line = output.decode().strip()
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
    logger.debug("Send input data: %s" % str(inputData))
    self.process.stdin.write(str(inputData) + '\n')
    self.process.stdin.flush()

  def _sendCommand(self, command, *args):
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
    while True:
      frame = self._readFrame(sock)
      if frame is None:
        logger.info("Disconnected from server.")
        break

      queue.put(frame)

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