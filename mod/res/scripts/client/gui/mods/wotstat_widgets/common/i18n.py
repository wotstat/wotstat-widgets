# -*- coding: utf-8 -*-
from helpers import getClientLanguage
from typing import List


def light(text):
  return '<font color="#e6e1c1">%s</font>' % text

def semilight(text):
  return '<font color="#c5c5b4">%s</font>' % text

RU = {
  'modslist.title': 'Добавить виджет',
  'modslist.description': 'Открыть меню добавления виджетов для мода WotStat',
  'notification.addWidget': '\n<a href=\"event:%s\">Добавить виджет</a>',
  'notification.addWidget.header': 'Виджеты от WotStat',
  'settings.add': 'Добавить',
  'settings.title': 'Добавить виджет',
  'settings.urlPlaceholder': 'Введите URL',
  'settings.collection': 'Коллекция виджетов',
  'settings.showUnpackError': 'Подробнее',
  'settings.addDemo': 'Демо виджет',
  'settings.info': 'Виджеты должны быть в формате веб-сайта или HTML файла. Вы можете добавить виджет по прямой ссылке (http:// или https://) или указать абсолютный путь к HTML файлу на вашем компьютере.',
  'settings.unpackingProcess': '100% (Распаковка)',
  'settings.platformNotSupported': 'К сожалению, ваша платформа %s не поддерживается.\n\nМод поддерживает только 64-битные версии Windows.',
  'settings.cannotUnpack': 'Не удалось распаковать необходимые компоненты. Вы можете попробовать сделать это вручную.',
  'settings.needUnpack': 'После первого запуска мода необходимо подготовить дополнительные файлы.',
  'settings.retrying': 'Произошла ошибка, попытка №%s: %s',
  'settings.error': 'Ошибка: ',
  'settings.pleaseWait': 'Пожалуйста подождите немного, этот процесс нужно выполнить только один раз.',
  'settings.downloading': 'Идёт загрузка: %s',
  'settings.runtimeError': 'Произошла ошибка при запуске сервиса обработки виджетов.',
  'settings.runtimeErrorContact': 'Если перезагрузка игры не поможет, обратитесь к разработчику мода в Discord @WotStat или support@wotstat.info',
  'settings.runtimeErrorButton': 'Частые проблемы',
  'changeUrl.title': 'Изменить URL',
  'changeUrl.urlPlaceholder': 'Введите URL',
  'changeUrl.apply': 'Применить',
  'changeUrl.cancel': 'Отмена',
  'whatsNew.title': 'Мод «WotStat Widgets» успешно обновлён до версии %s',
  'whatsNew.serverTitle': 'Новости мода «WotStat Widgets»',
  'context.lock': 'Заблокировать перемещение',
  'context.unlock': 'Разблокировать перемещение',
  'context.resize': 'Изменить размер',
  'context.endResize': 'Применить размер',
  'context.changeUrl': 'Изменить URL',
  'context.reload': 'Перезагрузить',
  'context.hideControls': 'Скрыть элементы управления',
  'context.showControls': 'Показать элементы управления',
  'context.clearData': 'Очистить данные',
  'context.clearData.apply': 'Подтвердить',
  'context.remove': 'Удалить виджет',
  'context.sendToTopPlan': 'На передний план',
  'context.position': 'Позиция: %s',
  'context.position.same': 'Одинаковая везде',
  'context.position.hangarBattle': 'Ангар/Бой',
  'context.position.hangarSniperArcade': 'Ангар/Снайп./Аркад.',
  'context.layer': 'Слой: %s',
  'context.layer.default': 'Обычный',
  'context.layer.top': 'Поверх всех',
}

EN = {
  'modslist.title': 'Add widget',
  'modslist.description': 'Open the widget add menu for the Widgets by WotStat mod',
  'notification.addWidget': '\n<a href=\"event:%s\">Add widget</a>',
  'notification.addWidget.header': 'Widgets by WotStat',
  'settings.add': 'Add',
  'settings.title': 'Add widget',
  'settings.urlPlaceholder': 'Enter URL',
  'settings.collection': 'Widgets collection',
  'settings.showUnpackError': 'How to',
  'settings.addDemo': 'Demo widget',
  'settings.info': 'Widgets should be in the format of a website or HTML file. You can add a widget by direct link (http:// or https://) or specify the absolute path to an HTML file on your computer.',
  'settings.unpackingProcess': '100% (Unpacking)',
  'settings.platformNotSupported': 'Unfortunately, your platform %s is not supported.\n\nThe mod only supports 64-bit versions of Windows.',
  'settings.cannotUnpack': 'Failed to unpack the necessary components. You can try to do it manually.',
  'settings.needUnpack': 'After the first launch of the mod, you need to prepare additional files.',
  'settings.retrying': 'An error occurred, attempt #%s: %s',
  'settings.error': 'Error: ',
  'settings.pleaseWait': 'Please wait a little, this process only needs to be done once.',
  'settings.downloading': 'Downloading: %s',
  'settings.runtimeError': 'An error occurred while starting the widgets process.',
  'settings.runtimeErrorContact': 'If restarting the game does not help, contact the mod developer via Discord @WotStat or support@wotstat.info',
  'settings.runtimeErrorButton': 'Common issues',
  'changeUrl.title': 'Change URL',
  'changeUrl.urlPlaceholder': 'Enter URL',
  'changeUrl.apply': 'Apply',
  'changeUrl.cancel': 'Cancel',
  'whatsNew.title': 'The \'WotStat Widgets\' mod has been successfully updated to version %s',
  'whatsNew.serverTitle': '\'WotStat Widgets\' mod news',
  'context.lock': 'Lock movement',
  'context.unlock': 'Unlock movement',
  'context.resize': 'Resize',
  'context.endResize': 'Apply size',
  'context.changeUrl': 'Change URL',
  'context.reload': 'Reload',
  'context.hideControls': 'Hide controls',
  'context.showControls': 'Show controls',
  'context.clearData': 'Clear data',
  'context.clearData.apply': 'Confirm',
  'context.remove': 'Remove widget',
  'context.sendToTopPlan': 'Bring to front',
  'context.position': 'Position: %s',
  'context.position.same': 'Same everywhere',
  'context.position.hangarBattle': 'Hangar/Battle',
  'context.position.hangarSniperArcade': 'Hangar/Sniper/Arcade',
  'context.layer': 'Layer: %s',
  'context.layer.default': 'Default',
  'context.layer.top': 'Top layer',
}

language = getClientLanguage()
currentLocalizations = RU

if language == 'ru':
  currentLocalizations = RU
else:
  currentLocalizations = EN


def t(key):
  if key in currentLocalizations:
    return currentLocalizations[key]
  return key

def getPreferredLanguage(values):
  # type: (List[str]) -> str
  
  if not values or len(values) == 0:
    return language
  
  if language in values:
    return language
  
  if 'ru' in values:
    return 'ru'
  
  return values[0]
