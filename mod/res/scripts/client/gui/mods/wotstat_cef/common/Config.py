import json
import os

from .Logger import Logger

VERSION = '{{VERSION}}'

logger = Logger.instance()

class Config:
  config = {}
  defaultParams = {
    'lokiURL': 'https://loki.wotstat.info/loki/api/v1/push',
  }

  def __init__(self, configPath, defaultParams=None):
    if defaultParams:
      self.defaultParams = defaultParams

    self.config = self.defaultParams.copy()

    try:
      if os.path.exists(configPath):
        with open(configPath, "r") as f:
          str = f.read()
          logger.debug('Found new config:\n%s' % str)
          parsed = json.loads(str)
          logger.debug('Parse new config:\n%s' % parsed)
          self.config.update(parsed)
          logger.info('Updated config:\n%s' % self.config)
    except Exception as e:
      logger.error('Load config error %s' % e)
    
    self.config['version'] = VERSION

  def get(self, key):
    return self.config[key] if key in self.config else self.defaultParams[
      key] if key in self.defaultParams else None
