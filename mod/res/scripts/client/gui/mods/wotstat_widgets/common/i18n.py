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
  'settings.addDemo': 'Демо виджет',
  'settings.info': 'Виджеты должны быть в формате веб-сайта или HTML файла. Вы можете добавить виджет по прямой ссылке (http:// или https://) или указать абсолютный путь к HTML файлу на вашем компьютере.',
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
  'settings.addDemo': 'Demo widget',
  'settings.info': 'Widgets should be in the format of a website or HTML file. You can add a widget by direct link (http:// or https://) or specify the absolute path to an HTML file on your computer.',
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
