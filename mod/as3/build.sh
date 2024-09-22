mxmlc -load-config+=build-config.xml src/wotstat/widgets/MainView.as
mxmlc -load-config+=build-config.xml --output=bin/wotstat.widgets.settings.swf src/wotstat/widgets/SettingsWindow.as
mxmlc -load-config+=build-config.xml --output=bin/wotstat.widgets.changeUrlWindow.swf src/wotstat/widgets/ChangeUrlWindow.as