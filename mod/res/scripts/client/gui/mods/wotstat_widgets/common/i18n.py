# -*- coding: utf-8 -*-
from helpers import getClientLanguage

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
}

language = getClientLanguage()
current_localizations = RU

if language == 'ru':
  current_localizations = RU
else:
  current_localizations = EN


def t(key):
  if key in current_localizations:
    return current_localizations[key]
  return key
