import subprocess
import threading

from ..common.Logger import Logger
from .constants import CEF_EXE_PATH

logger = Logger.instance()


class Commands:
  OPEN_NEW_BROWSER = 'OPEN_NEW_BROWSER'


class CefServer(object):

  enabled = False

  def __init__(self):
    pass

  def _readOutput(self):
    while self.enabled:
      output = self.process.stdout.readline()
      if output == '' and self.process.poll() is not None:
        continue

      if not output:
        continue

      line = output.decode().strip()
      if not line:
        continue

      if line.startswith('[DEBUG]'):
        logger.debug(line)
      elif line.startswith('[INFO]'):
        logger.info(line)
      elif line.startswith('[WARN]'):
        logger.warn(line)
      elif line.startswith('[ERROR]'):
        logger.error(line)
      else:
        logger.error('Unknown format: %s' % line)

  def _wrightInput(self, inputData):
    logger.debug("Send input data: %s" % str(inputData))
    print(self.process)
    print(self.process.stdin)
    self.process.stdin.write(str(inputData))
    self.process.stdin.flush()

  def _sendCommand(self, command, *args):
    cmd = command + ' ' + ' '.join([str(arg) for arg in args])
    self._wrightInput(str(cmd) + '\n')

  def enable(self):
    self.enabled = True
    startupInfo = subprocess.STARTUPINFO()
    startupInfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupInfo.wShowWindow = subprocess.SW_HIDE

    self.process = subprocess.Popen(CEF_EXE_PATH,
      startupinfo=startupInfo,
      stdin=subprocess.PIPE,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE)
    
    outputThread = threading.Thread(target=self._readOutput)
    outputThread.start()
    logger.info("CEF server started")

  def dispose(self):
    self.enabled = False
    self.process.terminate()
    logger.info("CEF server stopped")

  def openNewBrowser(self, url, port, width, height):
    self._sendCommand(Commands.OPEN_NEW_BROWSER, url, port, width, height)


server = CefServer()