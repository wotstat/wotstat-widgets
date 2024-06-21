# from gui.mods.wotstatWidget import createWidget

from .wotstat_cef.main.EventsManager import manager

def createWidget(url, port, width, height):
  manager.createWidget(url, port, width, height)

