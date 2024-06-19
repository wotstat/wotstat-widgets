# from gui.mods.wotstatWidget import createWidget

from .wotstat_cef.main.EventsManager import manager

def createWidget(url):
  manager.createWidget(url)

