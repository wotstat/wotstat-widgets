import os
import BigWorld
import json
from Singleton import Singleton
from gui import SystemMessages

from ..common.i18n import getPreferredLanguage, t, light
from ..common.Logger import Logger
from ..common.Notifier import Notifier
from ..common.PlayerPrefs import PlayerPrefs
from ..common.ExceptionHandling import withExceptionHandling
from ..constants import WIDGETS_COLLECTION_URL, ACTIVE_WIDGETS_PATH
from .SettingsWindow import show as showSettingsWindow
from .EventsManager import manager

openWebBrowser = BigWorld.wg_openWebBrowser if hasattr(BigWorld, 'wg_openWebBrowser') else BigWorld.openWebBrowser
logger = Logger.instance()
notifier = Notifier.instance()

LAST_SHOWED_RELEASE_NOTES_INDEX = 'LAST_SHOWED_RELEASE_NOTES_INDEX'
LAST_SHOWED_SERVER_NEWS_INDEX = 'LAST_SHOWED_SERVER_NEWS_INDEX'

class EventKeys():
  OPEN_SETTINGS = 'WOTSTAT_WIDGETS_EVENT_NEWS_OPEN_SETTINGS'
  ADD_WIDGET = 'WOTSTAT_WIDGETS_EVENT_NEWS_ADD_WIDGET:'
  OPEN_URL = 'WOTSTAT_WIDGETS_EVENT_NEWS_OPEN_URL:'

MOD_RELEASE_NOTES = [
  {
    'ru': 
      '<b>• Новое контекстное меню на ПКМ</b>\n'
      '    - Изменяйте URL\n'
      '    - Сбрасывайте данные\n'
      '    - Скрывайте элементы управления\n'
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
  {
    'ru':
      light('<b>• Раздельные позиции для аркадного и снайперского прицелов</b>') + ' – настраивается для каждого виджета ПКМ->Позиция\n' +
      light('<b>• Меняйте порядок слоёв</b>') + ' – ПКМ->На передний план\n' +
      light('<b>• Подтверждение сброса данных</b>\n') +
      light('<b>• Уменьшен минимальный размер виджета</b>'),
    'en':
      light('<b>• Separate positions for arcade and sniper scopes</b>') + ' – configured for each widget RMB->Position\n' +
      light('<b>• Change layers order</b>') + ' – RMB->Bring to front\n' +
      light('<b>• Confirmation of data reset</b>\n') +
      light('<b>• Reduced minimum widget size</b>')
  },
  {
    'ru': '• Исправлена ошибка определения взводов. Теперь взводные виджеты работают корректно',
    'en': '• Fixed platoon detection bug. Now platoon widgets work correctly'
  },
  {
    'ru': 
      '• Теперь мод корректно работает если по пути до игры присутствует кириллица\n' +
      '• Сохранение порядка виджетов\n'+
      '• Смена слоёв: ПКМ->Слой->Поверх всего\n' +
      '• Поддержка отступов: будет использовано в новых виджетах\n\n' +
      'А ещё добавлены улучшения для разработчиков виджетов и исправлено много ошибок',
    'en':
      '• Now the mod works correctly if there is Cyrillic in the path to the game\n' +
      '• Saving the order of widgets\n' +
      '• Change layers: RMB->Layer->Top layer\n' +
      '• Support for indents: will be used in new widgets\n\n' +
      'And also added improvements for widget developers and fixed many bugs'
  },
  {
    'ru': 'Исправлена ошибка, из-за которой свёрнутые ангарные виджеты отображались в бою',
    'en': 'Fixed a bug where collapsed hangar widgets were displayed in battle'
  },
  {
    'ru': 'Исправлена ошибка, из-за которой элементы управления могли отображаться в начале боя без нажатия клавиши CTRL',
    'en': 'Fixed a bug where controls could be displayed at the start of battle without pressing CTRL'
  }
]

class WhatsNewNotifier(Singleton):
  @staticmethod
  def instance():
    return WhatsNewNotifier()
  
  def _singleton_init(self):
    super(WhatsNewNotifier, self)._singleton_init()
    notifier.onEvent += self.onEvent
    
  def onEvent(self, event):
    # type: (str) -> None
    
    if event == EventKeys.OPEN_SETTINGS:
      showSettingsWindow()
    elif event.startswith(EventKeys.OPEN_URL):
      target = event.split(EventKeys.OPEN_URL)[1]
      logger.info('Opening browser from server news %s' % target)
      openWebBrowser(target)
    elif event.startswith(EventKeys.ADD_WIDGET):
      target = event.split(EventKeys.ADD_WIDGET)[1]
      logger.info('Opening widget from server news %s' % target)
      manager.createWidget(target, 170, -1)
      
  
  def showModNews(self, version):
    
    lastVisible = PlayerPrefs.getInt(LAST_SHOWED_RELEASE_NOTES_INDEX, -1)
    PlayerPrefs.set(LAST_SHOWED_RELEASE_NOTES_INDEX, len(MOD_RELEASE_NOTES) - 1)
    
    if lastVisible >= len(MOD_RELEASE_NOTES) - 1:
      return
    
    if lastVisible == -1:
      if not os.path.exists(ACTIVE_WIDGETS_PATH):
        return
    
    msg = ''
    for i in range(lastVisible + 1, len(MOD_RELEASE_NOTES)):
      msg += '\n' + MOD_RELEASE_NOTES[i].get(getPreferredLanguage(MOD_RELEASE_NOTES[i].keys()), '')
      
    if len(msg) == 0:
      return
    
    notifier.showNotification(msg, SystemMessages.SM_TYPE.InformationHeader, messageData={'header': t('whatsNew.title') % version}, priority='high')
  
  def showServerNews(self):
    def collectNews(notes):
      lastVisibleNote = PlayerPrefs.get(LAST_SHOWED_SERVER_NEWS_INDEX, None)
      lastNote = notes[len(notes) - 1]
      lastId = lastNote['id']
      PlayerPrefs.set(LAST_SHOWED_SERVER_NEWS_INDEX, str(lastId))
      
      if lastVisibleNote is None:
        logger.info('Never showed server news before. Skip to \'%s\'' % lastId)
        return
      
      if lastVisibleNote == str(lastId):
        logger.info('Already showed the latest server news. Skip')
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
        
      if len(lines) == 0:
        logger.info('No new server news to show')
        return
        
      msg = '\n' + '\n'.join(lines)
      notifier.showNotification(msg, SystemMessages.SM_TYPE.InformationHeader, messageData={'header': t('whatsNew.serverTitle')}, priority='high')
    
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