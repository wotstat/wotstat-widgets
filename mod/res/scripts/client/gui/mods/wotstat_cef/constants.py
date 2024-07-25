import os

CEF_PATH = os.path.join('mods', 'wotstat.widget.cef')
CEF_EXE_NAME = 'wotstat.widget.cef.exe'
CEF_EXE_PATH = os.path.join(os.path.abspath('.'), CEF_PATH, CEF_EXE_NAME)


CONFIG_PATH = './mods/configs/wotstat.widgets/config.cfg'
ACTIVE_WIDGETS_PATH = './mods/configs/wotstat.widgets/activeWidgets.json'

WOTSTAT_WIDGETS_EVENT_OPEN_SETTINGS = 'WOTSTAT_WIDGETS_EVENT_OPEN_SETTINGS'