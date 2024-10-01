from Singleton import Singleton

from ..common.i18n import getPreferredLanguage, t
from ..common.Logger import Logger
from ..common.Notifier import Notifier
from ..common.PlayerPrefs import PlayerPrefs
from ..common.ExceptionHandling import withExceptionHandling, SendExceptionEvent

logger = Logger.instance()
notifier = Notifier.instance()

LAST_SHOWED_RELEASE_NOTES_INDEX = 'LAST_SHOWED_RELEASE_NOTES_INDEX'

MOD_RELEASE_NOTES = [
  {
    'ru': '<b>• Новое контекстное меню на ПКМ</b>\n    - Изменяйте URL\n    - Сбрасывайте данные\n    - Скрывайте элементы управления в ангаре\n• Ангарные виджеты больше не отображаются в бою\n• Новые виджеты в бою по умолчанию отображаются в том месте, где вы их разместили в ангаре\n• Новая иконка замочка с переключением состояния открыт/закрыт',
    'en': '<b>• New context menu on right click</b>\n    - Change URL\n    - Reset widget\n    - Hide controls in hangar\n• Hangar widgets are no longer displayed in battle\n• New battle widgets are displayed by default in the same place where you placed them in the hangar\n• New lock icon with open/close state\n'
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
    logger.info("Showing server news")