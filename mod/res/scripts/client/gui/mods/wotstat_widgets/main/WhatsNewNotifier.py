import BigWorld
import json
from Singleton import Singleton

from ..common.i18n import getPreferredLanguage, t
from ..common.Logger import Logger
from ..common.Notifier import Notifier
from ..common.PlayerPrefs import PlayerPrefs
from ..common.ExceptionHandling import withExceptionHandling
from ..constants import WIDGETS_COLLECTION_URL

logger = Logger.instance()
notifier = Notifier.instance()

LAST_SHOWED_RELEASE_NOTES_INDEX = 'LAST_SHOWED_RELEASE_NOTES_INDEX'
LAST_SHOWED_SERVER_NEWS_INDEX = 'LAST_SHOWED_SERVER_NEWS_INDEX'

MOD_RELEASE_NOTES = [
  {
    'ru': 
      '<b>• Новое контекстное меню на ПКМ</b>\n'
      '    - Изменяйте URL\n'
      '    - Сбрасывайте данные\n'
      '    - Скрывайте элементы управления в ангаре\n'
      '• Ангарные виджеты больше не отображаются в бою\n'
      '• Новые виджеты в бою по умолчанию отображаются в том месте, где вы их разместили в ангаре\n'
      '• Новая иконка замочка с переключением состояния открыт/закрыт',
    'en': 
      '<b>• New context menu on right click</b>\n'
      '    - Change URL\n'
      '    - Reset widget\n'
      '    - Hide controls in hangar\n'
      '• Hangar widgets are no longer displayed in battle\n'
      '• New battle widgets are displayed by default in the same place where you placed them in the hangar\n'
      '• New lock icon with open/close state\n'
  },
]

class WhatsNewNotifier(Singleton):
  @staticmethod
  def instance():
    return WhatsNewNotifier()
  
  def showModNews(self, version):
    msg = t('whatsNew.title') % version
    
    lastVisible = PlayerPrefs.getInt(LAST_SHOWED_RELEASE_NOTES_INDEX, -1)
    
    if lastVisible >= len(MOD_RELEASE_NOTES) - 1:
      return
    
    for i in range(lastVisible + 1, len(MOD_RELEASE_NOTES)):
      msg += '\n' + MOD_RELEASE_NOTES[i].get(getPreferredLanguage(MOD_RELEASE_NOTES[i].keys()), '')
      
    PlayerPrefs.set(LAST_SHOWED_RELEASE_NOTES_INDEX, len(MOD_RELEASE_NOTES) - 1)
    
    notifier.showNotification(msg)
  
  def showServerNews(self):
    def collectNews(notes):
      lastVisibleNote = PlayerPrefs.get(LAST_SHOWED_SERVER_NEWS_INDEX, None)
      lastNote = notes[len(notes) - 1]
      lastId = lastNote['id']
      PlayerPrefs.set(LAST_SHOWED_SERVER_NEWS_INDEX, str(lastId))
      
      if lastVisibleNote is None:
        logger.info('Never showed server news before. Skip to \'%s\'' % lastId)
        return
      
      lastVisibleIndex = -1
      for i in range(len(notes)):
        if str(notes[i]['id']) == lastVisibleNote:
          lastVisibleIndex = i
          break
        
      if lastVisibleIndex == -1:
        logger.info('Can not find last visible server news. Skip to the last one')
        return
      
      lines = []
      for i in range(lastVisibleIndex + 1, len(notes)):
        targetLocalization = getPreferredLanguage(list(filter(lambda t: t != 'id', notes[i].keys())))
        lines.append(notes[i][targetLocalization])
        
      msg = t('whatsNew.serverTitle') + '\n'
      msg += '\n'.join(lines)
      notifier.showNotification(msg)
    
    @withExceptionHandling(logger)
    def onResponse(response):
      # type: (BigWorld.WGUrlResponse) -> None
      
      if response is None or response.responseCode != 200:
        logger.error('Failed to fetch server news')
        return
      
      try:
        data = json.loads(response.body)
        collectNews(data)
      except Exception as e:
        logger.error('Failed to parse server news response %s' % str(e))
    
    logger.info('Fetch server news')
    BigWorld.fetchURL(WIDGETS_COLLECTION_URL + '/release-notes.json', onResponse)