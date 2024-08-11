import BigWorld
from typing import Callable

from WebSocketDataProvider import WebSocketDataProvider
from DataProviderSDK import DataProviderSDK, DPExtension

from providers import setup as setupProviders

class PublicDataProviderSDK(object):
  version = 3
  
  def __init__(self, registerExtension, dispose):
    # type: (Callable[[str], DPExtension], Callable[[]]) -> None
    self.__registerExtension = registerExtension
    self.__dispose = dispose
    
  def registerExtension(self, extension):
    return self.__registerExtension(extension)
  
  def dispose(self):
    self.__dispose()
  

def setup(logger):

  def createSDK():
    dataProviderSDK = DataProviderSDK(WebSocketDataProvider(logger), logger)
    publicDataProviderSDK = PublicDataProviderSDK(dataProviderSDK.registerExtension, dataProviderSDK.dispose)
    BigWorld.wotstat_dataProvider = publicDataProviderSDK
    
    def nextFrame():
      if publicDataProviderSDK == BigWorld.wotstat_dataProvider:
        setupProviders(dataProviderSDK, logger)
        dataProviderSDK.setup()
        logger.info("DataProviderSDK providers setup complete")
      else:
        logger.info("DataProviderSDK has been replaced before setup")
    
    BigWorld.callback(0, nextFrame)
    
  
  if hasattr(BigWorld, 'wotstat_dataProvider'):
    version = BigWorld.wotstat_dataProvider.version
    if version < PublicDataProviderSDK.version:
      BigWorld.wotstat_dataProvider.dispose()
      createSDK()
      logger.info("DataProviderSDK updated from version %s to %s" % (version, PublicDataProviderSDK.version))
    else:
      logger.info("DataProviderSDK already exists with version %s" % version)
      
  else:
    createSDK()
    logger.info("DataProviderSDK created with version %s" % PublicDataProviderSDK.version)
  