import base64
import time
import hashlib
import os
import json

import BigWorld
from debug_utils import LOG_CURRENT_EXCEPTION
from constants import AUTH_REALM

from .Logger import ILoggerBackend, getLevelOrder, LEVELS_ORDER
from .crossGameUtils import readClientServerVersion

LEVELS_NAMES = list(LEVELS_ORDER.keys())

def prepareString(obj):
  if isinstance(obj, str):
    try:
      obj.decode('utf-8')
    except UnicodeDecodeError:
      return base64.b64encode(obj)
  return obj

def generate_session_id():
  current_time = str(time.time()).encode('utf-8')
  random_bytes = os.urandom(16)
  unique_bytes = current_time + random_bytes
  return hashlib.sha256(unique_bytes).hexdigest()

class ServerLoggerBackend(ILoggerBackend):
  __sendingQueue = []

  def __init__(self, url, prefix, source, modVersion, minLevel="INFO"):
    self.__minSendLevelOrder = getLevelOrder(minLevel)
    self.__url = url
    self.__prefix = prefix
    self.__source = source
    self.__modVersion = modVersion
    self.__gameVersion = readClientServerVersion()[1]
    if not self.__gameVersion: 
      self.__gameVersion = 'unknown_version'
    self.__sessionId = generate_session_id()

    self.__sendingLoop()

  def printLog(self, level, log):
    if getLevelOrder(level) >= self.__minSendLevelOrder:
      self.__send(level, log)
      
  def __send(self, level, msg):
    msg = prepareString(msg)
    self.__sendingQueue.append((int(time.time() * 1e9), level, msg))

  def __sendingLoop(self):
    BigWorld.callback(10, self.__sendingLoop)

    try:
      if len(self.__sendingQueue) == 0: return
      if not self.__url: return

      defaultStreamLabels = {
        "source": self.__source,
        "region": AUTH_REALM,
        "modVersion": self.__modVersion,
      }

      defaultStreamMeta = {
        "playerName": self.__get_player_name(),
        "gameVersion": self.__gameVersion,
        "session": self.__sessionId
      }

      streams = []

      for level in LEVELS_NAMES:
        current = filter(lambda msg: msg[1] == level, self.__sendingQueue)
        if len(current) == 0: continue

        streams.append({
          "stream": dict(defaultStreamLabels, level=level),
          "values": map(lambda msg: [str(msg[0]), msg[2], defaultStreamMeta], current)
        })

      postData = json.dumps({"streams": streams}, ensure_ascii=False)

      def sendCallback(res):
        # type: (BigWorld.WGUrlResponse) -> None
        if res is not None and res.responseCode != 200:
          print('%slogger sending error' % self.__prefix)
          print(res.body)

      BigWorld.fetchURL(url=self.__url,
                        callback=sendCallback,
                        headers={'Content-type': 'application/json', 'Accept': 'application/json'},
                        method='POST',
                        postData=postData)

    except Exception:
      print("%s[LOGGER EXCEPTION]" % self.__prefix)
      LOG_CURRENT_EXCEPTION()

    finally:
      self.__sendingQueue = []

  def __get_player_name(self):
    player = BigWorld.player()

    if not player: return 'unknown_player'
    if not player.name: return 'unknown_name'
    return player.name

