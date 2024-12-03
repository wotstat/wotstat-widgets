import os

CEF_PATH = os.path.join('mods', 'wotstat.widgets.cef')
CEF_EXE_NAME = 'wotstat.widgets.cef.exe'
CEF_EXE_PATH = os.path.join(CEF_PATH, CEF_EXE_NAME)


CONFIG_PATH = './mods/configs/wotstat.widgets/config.cfg'
ACTIVE_WIDGETS_PATH = './mods/configs/wotstat.widgets/activeWidgets.json'

WOTSTAT_WIDGETS_EVENT_OPEN_SETTINGS = 'WOTSTAT_WIDGETS_EVENT_OPEN_SETTINGS'
GITHUB_URL = 'https://api.github.com/repos/WOT-STAT/wotstat-widgets/releases/latest'
WIDGETS_COLLECTION_URL = 'https://widgets.wotstat.info'
# WIDGETS_COLLECTION_URL = 'http://192.168.0.4:5174'