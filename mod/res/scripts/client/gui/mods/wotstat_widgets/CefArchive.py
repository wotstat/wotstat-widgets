import os
from queue import Queue
import zipfile
import BigWorld
from Event import Event
import urllib2
import threading
import platform
import time
import tempfile

from .common.Logger import Logger

TEMP_CEF_ZIP_PATH = os.path.join(tempfile.gettempdir(), 'wotstat.widgets.cef.zip')
TARGET_CEF_PATH = 'mods/wotstat.widgets.cef'
TARGET_CEF_PATH_CHECKSUM = TARGET_CEF_PATH + '/checksum'

logger = Logger.instance()

class CefArchive():
  
  def __init__(self):
    self.enabled = True
    self.isReady = False
    self.progress = 0.0
    self.lastError = None
    self.retryCount = 0
    self.onProgressChange = Event()
    self.onError = Event()
    self.onReady = Event()
    self.downloadThread = None
        
  def setup(self, checksum):
    self.checksum = checksum
    logger.info('Setup CefArchive with checksum %s' % checksum)
    
    self.machine = platform.machine()
    if not self.machine.endswith('64'):
      logger.error('Unsupported platform %s' % self.machine)
      self._updateProgress(-2)
      return
      
    currentChecksum = None
    if os.path.exists(TARGET_CEF_PATH_CHECKSUM):
      with open(TARGET_CEF_PATH_CHECKSUM, 'r') as f:
        currentChecksum = f.read().strip()
        
    if currentChecksum == checksum:
      logger.info('CefArchive already exists with latest checksum %s' % checksum)
      self._onReady()
      return
    
    if currentChecksum is not None:
      logger.info('CefArchive checksum mismatch %s != %s' % (currentChecksum, checksum))
      
    self.downloadThread = self._downloadCef(TEMP_CEF_ZIP_PATH,
                      'https://storage.yandexcloud.net/wotstat-cef/wotstat.widgets.cef.%s.zip' % checksum)
    
  def dispose(self):
    self.enabled = False
    logger.info('CefArchive stopping')
    if self.downloadThread: self.downloadThread.join()
    logger.info('CefArchive stopped')
    
  def _updateProgress(self, progress):
    # type: (float) -> None
    self.progress = progress
    self.onProgressChange(progress)
  
  def _onReady(self):
    self.isReady = True
    self.onReady()
    logger.info('CefArchive is ready')
  
  def _downloadCef(self, target, url):
    logger.info('Download CEF from %s to %s' % (url, target))
    progressQueue = Queue()
    
    def unpack():
      with zipfile.ZipFile(target, 'r') as zip:
        zip.extractall('mods') 
    
    def downloadFile(chunk_size=1024):
      
      while self.retryCount < 3 and self.enabled:
        try:
          response = urllib2.urlopen(url)
          totalSize = int(response.info().getheader('Content-Length').strip())
          
          if totalSize == 0:
            logger.error('Download failed: 0 bytes')
            raise Exception('Download failed: 0 bytes')
          
          logger.info('Download started. Total size: %d' % totalSize)
          
          downloadedSize = 0
          
          directoryPath = os.path.dirname(target)
          if not os.path.exists(directoryPath): os.makedirs(directoryPath)
          if os.path.exists(target): os.remove(target)
          
          with open(target, 'wb') as f:
            while self.enabled:
              chunk = response.read(chunk_size)
              if not chunk: break
              f.write(chunk)
              downloadedSize += len(chunk)
              progress = float(downloadedSize) / totalSize
              progressQueue.put(progress)
              logger.info('Downloaded chunk %d bytes %d/%d (%s)' % (len(chunk), downloadedSize, totalSize, str(progress)))
            
          if downloadedSize == totalSize:
            logger.info('Download finished')
            progressQueue.put(1)
            time.sleep(1)
            progressQueue.put(1.5)
            logger.info('Unpack CEF')
            unpack()
            logger.info('Unpack CEF finished')
            progressQueue.put(2)
            break
          
        except Exception as e:
          self.lastError = 'Failed: %s' % str(e)
          self.retryCount += 1
          progressQueue.put(0)
          self.onError(self.lastError)
          logger.error(self.lastError)
      
          if self.retryCount == 3:
            logger.error('Download failed after 3 retries')
            progressQueue.put(-1)
            break
            
          time.sleep(3)
          logger.info('Retry download %d' % self.retryCount)
      
      logger.info('Download thread end')

    def mainThreadProcess():
        
      if not progressQueue.empty():
        lastValue = 0
        while not progressQueue.empty():
          lastValue = progressQueue.get()
          
        self._updateProgress(lastValue)

        if lastValue == 2:
          self._onReady()
          self.enabled = False
          return
        
        if lastValue == -1:
          return
    
      if self.enabled:
        BigWorld.callback(0.1, mainThreadProcess)
      
    thread = threading.Thread(target=downloadFile, args=(1024*1024*1,))
    thread.start()
    mainThreadProcess()
    return thread
        
cefArchive = CefArchive()