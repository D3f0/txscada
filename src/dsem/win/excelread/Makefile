# Makefile para los recursos y la interfase
# de pyqt

.PHONY : recursos gui

all: recursos gui

recursos: data_rc.py

data_rc.py: gui/ui_files/data.qrc
	pyrcc4 -compress 9 $^ -o $@ 

gui: gui/ui_mainwindow.py

gui/ui_mainwindow.py: gui/ui_files/mainwindow.ui
	pyuic4 $^ -o $@ -x

