# Archivo de consturccion del proyecto

PYUIC = $(shell which pyuic || which pyuic4)
PYRCC = $(shell which pyrcc || which pyrcc4)


.PHONY: resoruces uis

all: resources uis

resources: res_rc.py

res_rc.py:	res.qrc
	$(PYRCC) $^ -o $@
	

uis: gui/ui_mainwin.py


gui/ui_mainwin.py: gui/ui_files/mainwin.ui
	${PYUIC} $^ -o $@ -x

exedir:


exefile:

