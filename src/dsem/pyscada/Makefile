# Definiciones
PYUIC = pyuic4
PYRCC = pyrcc4
UIS = $(patsubst gui\/ui_files\/%,%,$(basename $(patsubst %.ui,%.py,$(wildcard gui/ui_files/*.ui))))
# Esta online es feo, pero es más fácil que hacer usar la sinstaxis de GNU Make
# para crear los targets.
UIS_NAMES = $(shell python -c "print ' '.join(map(lambda x: x.replace('ui_files/','ui_')+'.py','$(UIS)'.split()))")

# ifeq ($(OS),Windows_NT)
# 	@echo "Hola mundo"
# endif

all: recursos $(UIS_NAMES)
	@echo Sistema operativo: $(OS)
	

recursos: data_rc.py

	
data_rc.py: data.qrc
	${PYRCC} $^ -o $@
	
gui/ui_%.py: gui/ui_files/%.ui
	${PYUIC} $^ -o $@ -x
