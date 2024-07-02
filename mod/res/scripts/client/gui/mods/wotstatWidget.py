# from gui.mods.wotstatWidget import createWidget

from .wotstat_cef.main.EventsManager import manager

def createWidget(url, width=500):
  manager.createWidget(url, width)

