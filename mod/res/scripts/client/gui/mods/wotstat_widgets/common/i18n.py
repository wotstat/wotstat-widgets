# -*- coding: utf-8 -*-
from helpers import getClientLanguage
from typing import List

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
  'settings.runtimeError': 'Произошла ошибка при запуске сервиса обработки виджетов. Попробуйте перезапустить игру.\nЕсли ошибка повторяется, обратитесь к разработчику мода (@WotStat в Discord или по почте support@wotstat.info)',
  'changeUrl.title': 'Изменить URL',
  'changeUrl.urlPlaceholder': 'Введите URL',
  'changeUrl.apply': 'Применить',
  'changeUrl.cancel': 'Отмена',
  'whatsNew.title': 'Мод <b>WotStat Widgets</b> успешно обновлён до версии <b>%s</b>\n\nИзменения:',
  'whatsNew.serverTitle': 'Новости мода <b>WotStat Widgets</b>\n\nЧто нового:',
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
  'settings.runtimeError': 'An error occurred while starting the widget processing service. Try restarting the game.\nIf the error persists, contact the mod developer (@WotStat on Discord or by email support@wotstat.info)',
  'changeUrl.title': 'Change URL',
  'changeUrl.urlPlaceholder': 'Enter URL',
  'changeUrl.apply': 'Apply',
  'changeUrl.cancel': 'Cancel',
  'whatsNew.title': 'The <b>WotStat Widgets</b> mod has been successfully updated to version <b>%s</b>\n\nChanges:',
  'whatsNew.serverTitle': '<b>WotStat Widgets</b> mod news\n\nWhat\'s new:',
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
