import os
import shutil
import json
import re
import random
from datetime import datetime

import BigWorld
from helpers import getShortClientVersion
from .ExceptionHandling import withExceptionHandling

from .Logger import Logger

GH_HEADERS = {
  'X-GitHub-Api-Version': '2022-11-28',
  'Accept': 'application/vnd.github+json',
  'User-Agent': 'WOT/client',
}

logger = Logger.instance()

def _numericVersion():
  return getShortClientVersion().split('v.')[1].strip()

class UpdateStatus:
  NOT_OK_RESPONSE = 'NOT_OK_RESPONSE'
  BAD_INFO = 'BAD_INFO'
  ALREADY_UP_TO_DATE = 'ALREADY_UP_TO_DATE'
  SKIP_BY_CANARY = 'SKIP_BY_CANARY'
  UPDATED = 'UPDATED'

class ModUpdater(object):

  def __init__(self, modName, currentVersion, ghUrl):
    self.modName = modName
    self.ghUrl = ghUrl
    self.currentVersion = currentVersion

  def getFullModName(self, version=None):
    return self.modName + '_' + (version if version else self.currentVersion) + '.wotmod'
  
  def copyToNextVersions(self): 
    gameVersion = _numericVersion()
    currentMod = os.path.join(os.path.abspath('./mods/'), gameVersion, self.getFullModName())

    def increaseVersion(version, index):
      return '.'.join(
        [str(int(current) + 1 if i == index else 0) if i >= index else current for i, current in enumerate(version.split('.'))])

    v = [increaseVersion(gameVersion, i) for i in range(1, len(gameVersion.split('.')))]

    absPath = os.path.abspath('./mods/')
    for i in range(len(v)):
      p = os.path.join(absPath, v[i])
      if not os.path.exists(p):
        os.mkdir(p)
      filePath = os.path.join(p, self.getFullModName())
      if not os.path.exists(filePath):
        shutil.copyfile(currentMod, filePath)
  
  @withExceptionHandling(logger)
  def updateToGitHubReleases(self, onComplete=None):

    def onCompleteInvoke(status):
      if onComplete:
        onComplete(status)
    
    @withExceptionHandling(logger)
    def onEndDownload(latestVersion, data):
      # type: (str, BigWorld.WGUrlResponse) -> None
      if data.responseCode != 200:
        logger.error('GH Update. Download response status is not 200: %s' % data.responseCode)
        return onCompleteInvoke(UpdateStatus.NOT_OK_RESPONSE)
        
    
      gameVersion = _numericVersion()
      newModPath = os.path.join(os.path.abspath('./mods/'), gameVersion, self.getFullModName(latestVersion))
      if not os.path.exists(newModPath):
        with open(newModPath, "wb") as f:
          f.write(data.body)

      onCompleteInvoke(UpdateStatus.UPDATED)

    @withExceptionHandling(logger)
    def onResponse(data):
      # type: (BigWorld.WGUrlResponse) -> None
      
      if data.responseCode != 200:
        logger.error('GH Update. Response status is not 200: %s' % data.responseCode)
        return onCompleteInvoke(UpdateStatus.NOT_OK_RESPONSE)
      
      parsed = json.loads(data.body)
      latestVersion = parsed['tag_name']
      logger.info('GH Update. Latest version: %s' % latestVersion)

      if latestVersion == self.currentVersion:
        logger.debug('GH Update. Already up to date')
        return onCompleteInvoke(UpdateStatus.ALREADY_UP_TO_DATE)
      
      match = re.search('`canary_upgrade=(\d+.\d+|\d+)?`', parsed['body'])
      numCanaryUpgrade = float(match.group(1)) if match else None

      if numCanaryUpgrade is not None:
        publishedAt = parsed['published_at']
        parsed_date = datetime.strptime(publishedAt, "%Y-%m-%dT%H:%M:%SZ")
        now = datetime.now()
        delta = now - parsed_date
        day_since_release = max(delta.days + 1, 1)

        update_fraction_today = 1 - (1 - numCanaryUpgrade) ** day_since_release
        rnd = random.random()

        logger.info('GH Update. Update canary fraction today: %s; RND=%s' % (update_fraction_today, rnd))

        if rnd > update_fraction_today:
          return onCompleteInvoke(UpdateStatus.SKIP_BY_CANARY)

      else:
        logger.error('GH Update. Can not parse canary_upgrade in release notes')

      assets = parsed['assets']
      asset = filter(lambda x: ('name' in x) and (x['name'] == self.modName + '_' + latestVersion + '.wotmod'), assets)
      if not len(asset) > 0:
        logger.error('GH Update. Can not find asset for version: %s' % latestVersion)
        return onCompleteInvoke(UpdateStatus.BAD_INFO)
        

      firstAsset = asset[0]
      if 'browser_download_url' not in firstAsset:
        logger.error('GH Update. Can not find browser_download_url in asset')
        return onCompleteInvoke(UpdateStatus.BAD_INFO)
        
      downloadUrl = firstAsset['browser_download_url']
      logger.info('GH Update. Download url: %s' % downloadUrl)

      BigWorld.fetchURL(downloadUrl, lambda data: onEndDownload(latestVersion, data))
    
    BigWorld.fetchURL(self.ghUrl, onResponse, GH_HEADERS)
