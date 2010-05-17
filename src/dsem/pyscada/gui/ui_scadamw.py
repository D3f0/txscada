# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui/ui_files/scadamw.ui'
#
# Created: Mon Apr  6 04:59:32 2009
#      by: PyQt4 UI code generator 4.4.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(820, 627)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/res/logo.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabs = QtGui.QTabWidget(self.centralwidget)
        self.tabs.setTabShape(QtGui.QTabWidget.Rounded)
        self.tabs.setObjectName("tabs")
        self.tab_map = QtGui.QWidget()
        self.tab_map.setObjectName("tab_map")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.tab_map)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.splitter = QtGui.QSplitter(self.tab_map)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.graphicsViewMap = MapView(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(200)
        sizePolicy.setHeightForWidth(self.graphicsViewMap.sizePolicy().hasHeightForWidth())
        self.graphicsViewMap.setSizePolicy(sizePolicy)
        self.graphicsViewMap.setMinimumSize(QtCore.QSize(0, 400))
        self.graphicsViewMap.setObjectName("graphicsViewMap")
        self.verticalLayout_2.addWidget(self.splitter)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/res/applications-internet.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tabs.addTab(self.tab_map, icon1, "")
        self.tab_events = QtGui.QWidget()
        self.tab_events.setObjectName("tab_events")
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.tab_events)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.splitter_2 = QtGui.QSplitter(self.tab_events)
        self.splitter_2.setOrientation(QtCore.Qt.Vertical)
        self.splitter_2.setObjectName("splitter_2")
        self.groupBox = QtGui.QGroupBox(self.splitter_2)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_5 = QtGui.QHBoxLayout(self.groupBox)
        self.horizontalLayout_5.setSpacing(1)
        self.horizontalLayout_5.setMargin(1)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.tableHighPrio = QTableViewHighPrio(self.groupBox)
        self.tableHighPrio.setObjectName("tableHighPrio")
        self.horizontalLayout_5.addWidget(self.tableHighPrio)
        self.groupBox_2 = QtGui.QGroupBox(self.splitter_2)
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout_6 = QtGui.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_6.setSpacing(1)
        self.horizontalLayout_6.setMargin(1)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.tableLowPrio = QTableViewLowPrio(self.groupBox_2)
        self.tableLowPrio.setObjectName("tableLowPrio")
        self.horizontalLayout_6.addWidget(self.tableLowPrio)
        self.verticalLayout_6.addWidget(self.splitter_2)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/res/application-vnd.oasis.opendocument.spreadsheet.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tabs.addTab(self.tab_events, icon2, "")
        self.tab_conf = QtGui.QWidget()
        self.tab_conf.setObjectName("tab_conf")
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.tab_conf)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.toolBox_configuracion_comandos = QtGui.QToolBox(self.tab_conf)
        self.toolBox_configuracion_comandos.setFrameShape(QtGui.QFrame.StyledPanel)
        self.toolBox_configuracion_comandos.setFrameShadow(QtGui.QFrame.Raised)
        self.toolBox_configuracion_comandos.setObjectName("toolBox_configuracion_comandos")
        self.pageComs = QtGui.QWidget()
        self.pageComs.setGeometry(QtCore.QRect(0, 0, 786, 423))
        self.pageComs.setObjectName("pageComs")
        self.verticalLayout_9 = QtGui.QVBoxLayout(self.pageComs)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.verticalLayout_8 = QtGui.QVBoxLayout()
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.label_2 = QtGui.QLabel(self.pageComs)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_8.addWidget(self.label_2)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_6 = QtGui.QLabel(self.pageComs)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_4.addWidget(self.label_6)
        self.comboBox_concentrador = QComboBoxModelQuery(self.pageComs)
        self.comboBox_concentrador.setObjectName("comboBox_concentrador")
        self.horizontalLayout_4.addWidget(self.comboBox_concentrador)
        self.label_4 = QtGui.QLabel(self.pageComs)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_4.addWidget(self.label_4)
        self.comboPgmZona = QtGui.QComboBox(self.pageComs)
        self.comboPgmZona.setObjectName("comboPgmZona")
        self.horizontalLayout_4.addWidget(self.comboPgmZona)
        self.label_5 = QtGui.QLabel(self.pageComs)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_4.addWidget(self.label_5)
        self.comboPgmUc = QtGui.QComboBox(self.pageComs)
        self.comboPgmUc.setObjectName("comboPgmUc")
        self.horizontalLayout_4.addWidget(self.comboPgmUc)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.pushButton_prog_manual = QtGui.QPushButton(self.pageComs)
        self.pushButton_prog_manual.setObjectName("pushButton_prog_manual")
        self.horizontalLayout_4.addWidget(self.pushButton_prog_manual)
        self.pushButton_prog_auto = QtGui.QPushButton(self.pageComs)
        self.pushButton_prog_auto.setObjectName("pushButton_prog_auto")
        self.horizontalLayout_4.addWidget(self.pushButton_prog_auto)
        self.verticalLayout_8.addLayout(self.horizontalLayout_4)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_8.addItem(spacerItem1)
        self.verticalLayout_9.addLayout(self.verticalLayout_8)
        self.toolBox_configuracion_comandos.addItem(self.pageComs, "")
        self.pageCOs = QtGui.QWidget()
        self.pageCOs.setGeometry(QtCore.QRect(0, 0, 786, 423))
        self.pageCOs.setObjectName("pageCOs")
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.pageCOs)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.verticalLayout_7 = QtGui.QVBoxLayout()
        self.verticalLayout_7.setSpacing(2)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label = QtGui.QLabel(self.pageCOs)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.pushAddCO = QtGui.QPushButton(self.pageCOs)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icons/res/list-add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushAddCO.setIcon(icon3)
        self.pushAddCO.setObjectName("pushAddCO")
        self.horizontalLayout_3.addWidget(self.pushAddCO)
        self.verticalLayout_7.addLayout(self.horizontalLayout_3)
        self.tableCO = QTableCO(self.pageCOs)
        self.tableCO.setObjectName("tableCO")
        self.verticalLayout_7.addWidget(self.tableCO)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_3 = QtGui.QLabel(self.pageCOs)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_2.addWidget(self.label_3)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem3)
        self.toolAddUC = QtGui.QToolButton(self.pageCOs)
        self.toolAddUC.setObjectName("toolAddUC")
        self.horizontalLayout_2.addWidget(self.toolAddUC)
        self.verticalLayout_7.addLayout(self.horizontalLayout_2)
        self.tableUC = QTableUC(self.pageCOs)
        self.tableUC.setObjectName("tableUC")
        self.verticalLayout_7.addWidget(self.tableUC)
        self.verticalLayout_5.addLayout(self.verticalLayout_7)
        self.toolBox_configuracion_comandos.addItem(self.pageCOs, "")
        self.verticalLayout_4.addWidget(self.toolBox_configuracion_comandos)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/icons/res/configure.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tabs.addTab(self.tab_conf, icon4, "")
        self.verticalLayout.addWidget(self.tabs)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 820, 24))
        self.menubar.setObjectName("menubar")
        self.menuSCADA = QtGui.QMenu(self.menubar)
        self.menuSCADA.setObjectName("menuSCADA")
        self.menuOptions = QtGui.QMenu(self.menubar)
        self.menuOptions.setObjectName("menuOptions")
        self.menuBarra_de_herramientas = QtGui.QMenu(self.menuOptions)
        self.menuBarra_de_herramientas.setObjectName("menuBarra_de_herramientas")
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        self.menuAdmin = QtGui.QMenu(self.menubar)
        self.menuAdmin.setObjectName("menuAdmin")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.scadaToolbar = QtGui.QToolBar(MainWindow)
        self.scadaToolbar.setIconSize(QtCore.QSize(32, 32))
        self.scadaToolbar.setObjectName("scadaToolbar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.scadaToolbar)
        self.toolBar_mapa = QtGui.QToolBar(MainWindow)
        self.toolBar_mapa.setIconSize(QtCore.QSize(32, 32))
        self.toolBar_mapa.setObjectName("toolBar_mapa")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar_mapa)
        self.toolBar_mapa_visor = QtGui.QToolBar(MainWindow)
        self.toolBar_mapa_visor.setIconSize(QtCore.QSize(32, 32))
        self.toolBar_mapa_visor.setObjectName("toolBar_mapa_visor")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar_mapa_visor)
        self.toolBar_debug = QtGui.QToolBar(MainWindow)
        self.toolBar_debug.setIconSize(QtCore.QSize(32, 32))
        self.toolBar_debug.setObjectName("toolBar_debug")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar_debug)
        self.toolBar_impresion = QtGui.QToolBar(MainWindow)
        self.toolBar_impresion.setIconSize(QtCore.QSize(32, 32))
        self.toolBar_impresion.setObjectName("toolBar_impresion")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar_impresion)
        self.actionAbout = QtGui.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionAbout_Qt = QtGui.QAction(MainWindow)
        self.actionAbout_Qt.setObjectName("actionAbout_Qt")
        self.actionQuit = QtGui.QAction(MainWindow)
        self.actionQuit.setObjectName("actionQuit")
        self.actionStart = QtGui.QAction(MainWindow)
        self.actionStart.setCheckable(True)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/icons/res/player-time.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionStart.setIcon(icon5)
        self.actionStart.setObjectName("actionStart")
        self.actionStop = QtGui.QAction(MainWindow)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/icons/res/process-stop.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionStop.setIcon(icon6)
        self.actionStop.setObjectName("actionStop")
        self.actionSCADA_Config = QtGui.QAction(MainWindow)
        self.actionSCADA_Config.setIcon(icon4)
        self.actionSCADA_Config.setObjectName("actionSCADA_Config")
        self.actionLogs = QtGui.QAction(MainWindow)
        self.actionLogs.setObjectName("actionLogs")
        self.actionMapa = QtGui.QAction(MainWindow)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/icons/res/applications-accessories.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionMapa.setIcon(icon7)
        self.actionMapa.setObjectName("actionMapa")
        self.actionEdici_n_Esquina = QtGui.QAction(MainWindow)
        self.actionEdici_n_Esquina.setObjectName("actionEdici_n_Esquina")
        self.actionUsuario = QtGui.QAction(MainWindow)
        self.actionUsuario.setObjectName("actionUsuario")
        self.actionDBUrl = QtGui.QAction(MainWindow)
        self.actionDBUrl.setObjectName("actionDBUrl")
        self.actionScada = QtGui.QAction(MainWindow)
        self.actionScada.setCheckable(True)
        self.actionScada.setChecked(True)
        self.actionScada.setObjectName("actionScada")
        self.actionIO = QtGui.QAction(MainWindow)
        self.actionIO.setCheckable(True)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/icons/res/strigi.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionIO.setIcon(icon8)
        self.actionIO.setObjectName("actionIO")
        self.actionLimpiar_Eventos = QtGui.QAction(MainWindow)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(":/icons/res/draw-eraser.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionLimpiar_Eventos.setIcon(icon9)
        self.actionLimpiar_Eventos.setObjectName("actionLimpiar_Eventos")
        self.actionImprimir = QtGui.QAction(MainWindow)
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap(":/icons/res/printer.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionImprimir.setIcon(icon10)
        self.actionImprimir.setObjectName("actionImprimir")
        self.menuSCADA.addAction(self.actionUsuario)
        self.menuSCADA.addAction(self.actionStart)
        self.menuSCADA.addAction(self.actionStop)
        self.menuSCADA.addAction(self.actionQuit)
        self.menuBarra_de_herramientas.addAction(self.actionScada)
        self.menuOptions.addAction(self.actionSCADA_Config)
        self.menuOptions.addAction(self.actionLogs)
        self.menuOptions.addAction(self.actionDBUrl)
        self.menuOptions.addAction(self.menuBarra_de_herramientas.menuAction())
        self.menuHelp.addAction(self.actionAbout)
        self.menuHelp.addAction(self.actionAbout_Qt)
        self.menuAdmin.addAction(self.actionMapa)
        self.menubar.addAction(self.menuSCADA.menuAction())
        self.menubar.addAction(self.menuAdmin.menuAction())
        self.menubar.addAction(self.menuOptions.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.scadaToolbar.addAction(self.actionStart)
        self.scadaToolbar.addAction(self.actionStop)
        self.toolBar_mapa.addAction(self.actionMapa)
        self.toolBar_debug.addAction(self.actionIO)
        self.toolBar_debug.addAction(self.actionLimpiar_Eventos)
        self.toolBar_debug.addAction(self.actionSCADA_Config)
        self.toolBar_impresion.addAction(self.actionImprimir)

        self.retranslateUi(MainWindow)
        self.tabs.setCurrentIndex(2)
        self.toolBox_configuracion_comandos.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Semforización", None, QtGui.QApplication.UnicodeUTF8))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_map), QtGui.QApplication.translate("MainWindow", "&Mapa", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("MainWindow", "Eventos de muy alta prioridad y alta prioridad", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("MainWindow", "Eventos de baja prioridad y muy baja prioridad", None, QtGui.QApplication.UnicodeUTF8))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_events), QtGui.QApplication.translate("MainWindow", "&Eventos", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'DejaVu Sans\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Cambio de programa</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("MainWindow", "Concentrador", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("MainWindow", "Zona:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("MainWindow", "UC:", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_prog_manual.setText(QtGui.QApplication.translate("MainWindow", "Programa Manual", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_prog_auto.setText(QtGui.QApplication.translate("MainWindow", "Programa automático", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBox_configuracion_comandos.setItemText(self.toolBox_configuracion_comandos.indexOf(self.pageComs), QtGui.QApplication.translate("MainWindow", "C&omandos", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'DejaVu Sans\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Concentradores</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'DejaVu Sans\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Unidades de Control</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.toolAddUC.setText(QtGui.QApplication.translate("MainWindow", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBox_configuracion_comandos.setItemText(self.toolBox_configuracion_comandos.indexOf(self.pageCOs), QtGui.QApplication.translate("MainWindow", "Concentradores y &Unidades de Control", None, QtGui.QApplication.UnicodeUTF8))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_conf), QtGui.QApplication.translate("MainWindow", "&Configuracion", None, QtGui.QApplication.UnicodeUTF8))
        self.menuSCADA.setTitle(QtGui.QApplication.translate("MainWindow", "&SCADA", None, QtGui.QApplication.UnicodeUTF8))
        self.menuOptions.setTitle(QtGui.QApplication.translate("MainWindow", "&Herramientas", None, QtGui.QApplication.UnicodeUTF8))
        self.menuBarra_de_herramientas.setTitle(QtGui.QApplication.translate("MainWindow", "Barra de herramientas", None, QtGui.QApplication.UnicodeUTF8))
        self.menuHelp.setTitle(QtGui.QApplication.translate("MainWindow", "A&yuda", None, QtGui.QApplication.UnicodeUTF8))
        self.menuAdmin.setTitle(QtGui.QApplication.translate("MainWindow", "&Administración", None, QtGui.QApplication.UnicodeUTF8))
        self.scadaToolbar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "SCADA", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBar_mapa.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Edición de mapa", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBar_mapa_visor.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Visor de mapa", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBar_debug.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Debug", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBar_impresion.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Impresión", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout.setText(QtGui.QApplication.translate("MainWindow", "Sobre...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout_Qt.setText(QtGui.QApplication.translate("MainWindow", "Sobre Qt...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionQuit.setText(QtGui.QApplication.translate("MainWindow", "Quit", None, QtGui.QApplication.UnicodeUTF8))
        self.actionStart.setText(QtGui.QApplication.translate("MainWindow", "Start", None, QtGui.QApplication.UnicodeUTF8))
        self.actionStart.setStatusTip(QtGui.QApplication.translate("MainWindow", "Inicia el motor scada", None, QtGui.QApplication.UnicodeUTF8))
        self.actionStop.setText(QtGui.QApplication.translate("MainWindow", "Stop", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSCADA_Config.setText(QtGui.QApplication.translate("MainWindow", "SCADA Config", None, QtGui.QApplication.UnicodeUTF8))
        self.actionLogs.setText(QtGui.QApplication.translate("MainWindow", "Logs", None, QtGui.QApplication.UnicodeUTF8))
        self.actionMapa.setText(QtGui.QApplication.translate("MainWindow", "Edición Mapa", None, QtGui.QApplication.UnicodeUTF8))
        self.actionEdici_n_Esquina.setText(QtGui.QApplication.translate("MainWindow", "Edición Esquina", None, QtGui.QApplication.UnicodeUTF8))
        self.actionUsuario.setText(QtGui.QApplication.translate("MainWindow", "Cambio de usuario", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDBUrl.setText(QtGui.QApplication.translate("MainWindow", "Mostrar RFC1783 DB URL", None, QtGui.QApplication.UnicodeUTF8))
        self.actionScada.setText(QtGui.QApplication.translate("MainWindow", "Scada", None, QtGui.QApplication.UnicodeUTF8))
        self.actionIO.setText(QtGui.QApplication.translate("MainWindow", "DebugIO", None, QtGui.QApplication.UnicodeUTF8))
        self.actionLimpiar_Eventos.setText(QtGui.QApplication.translate("MainWindow", "Limpiar Eventos", None, QtGui.QApplication.UnicodeUTF8))
        self.actionImprimir.setText(QtGui.QApplication.translate("MainWindow", "Imprimir", None, QtGui.QApplication.UnicodeUTF8))

from widgets import QComboBoxModelQuery
from mapview import MapView
from dbview import QTableViewHighPrio, QTableCO, QTableUC, QTableViewLowPrio
import data_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

