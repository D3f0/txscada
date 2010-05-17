#! /usr/bin/env python
# -*- encoding: utf-8 -*-
from dscada.lib import main_is_frozen
from winlauncher.serverthread import ServerThread

import sys, os

from PyQt4 import QtCore, QtGui
from winlauncher.gui.configwindow import ConfigDialog

class UcnetTrayIcon(QtGui.QSystemTrayIcon):
    ''' Icono de la barra de tareas '''
    def __init__(self, *largs):
        
        QtGui.QSystemTrayIcon.__init__(self, *largs) # Superclase
        
        # Alias a la app
        self.app = QtGui.QApplication.instance()
        
        # Generamos las acciones y las conectamos
        self.setup_actions()
        # Generamos los menus
        self.setup_menus()
        self.setIcon(QtGui.QIcon('res/trayicon/icon.png'))
        self.config_window = None
        self.setToolTip(u"Launcher de µC Net Web HMI")
        # Conectar los on_<Qobject_name>_action
        self.server = ServerThread()
        self.connect(self.server, QtCore.SIGNAL("started()"), self.started)
        self.connect(self.server, QtCore.SIGNAL("stoped()"), self.stoped)
        self.connect(self.server, QtCore.SIGNAL("aborted"), self.aborted)
        
        QtCore.QMetaObject.connectSlotsByName(self)
        
    def setup_actions(self):
        self.action_config = QtGui.QAction(self.trUtf8("Configurar"), self)
        self.connect(self.action_config, QtCore.SIGNAL("triggered()"),
                     self.do_config)
        # TODO: Setear el ícono para la configuración
        self.action_quit = QtGui.QAction(self.trUtf8("Salir"), self)
        self.connect(self.action_quit, QtCore.SIGNAL("triggered()"), 
                     self.do_quit)
        
        self.connect(self, QtCore.SIGNAL("activated(QSystemTrayIcon::ActivationReason)"),
                     self.do_handle_activation)
        
        self.action_start = QtGui.QAction(self.trUtf8("Iniciar eservidor"), self)
        self.connect(self.action_start, QtCore.SIGNAL("triggered()"), self.start_server)
        self.action_start.setEnabled(True)
        
        self.action_stop = QtGui.QAction(self.trUtf8("Detener servidor"), self)
        self.connect(self.action_stop, QtCore.SIGNAL("triggered()"), self.stop_server)
        self.action_stop.setEnabled(False)
        self.action_restart = QtGui.QAction(self.trUtf8("Reiniciar servidor"), self)
        self.connect(self.action_restart, QtCore.SIGNAL("triggered()"), self.restart_server)
        self.action_restart.setEnabled(False)
        # Íconos
        self.action_quit.setIcon(QtGui.QIcon("res/oxy/actions/window-close.png"))
        
        self.action_config.setIcon(QtGui.QIcon("res/oxy/actions/configure-shortcuts.png"))
        
        self.action_start.setIcon(QtGui.QIcon("res/oxy/actions/arrow-right.png"))
        self.action_stop.setIcon(QtGui.QIcon("res/oxy/actions/process-stop.png"))
        self.action_restart.setIcon(QtGui.QIcon("res/oxy/actions/view-refresh.png"))
        
        # Menú de configuración rápida
        
        self.action_opt_open_browser = QtGui.QAction(self.trUtf8("Abrir browser al iniciar servidor"), self)
        self.action_opt_open_browser.setCheckable(True)
        self.action_opt_open_browser.setObjectName("opt_open_browser")
        
        self.action_opt_open_browser.setChecked( self.app.start_browser )
        
        port = self.app.port
        self.action_opt_server_port = QtGui.QAction(self.trUtf8("Puerto %d" % port), self)
        self.action_opt_server_port.setObjectName("opt_server_port")
        
    def setup_menus(self):
        # Definimos las acciones del menú y su orden
        self.menu = QtGui.QMenu()
        self.menu.addAction(self.action_start)
        self.menu.addAction(self.action_stop)
        self.menu.addAction(self.action_restart)
        self.menu.addSeparator()
        opts_menu = self.menu.addMenu(self.trUtf8("Opciones"))
        opts_menu.addAction(self.action_opt_open_browser)
        opts_menu.addAction(self.action_opt_server_port)
        self.menu.addSeparator()
        self.menu.addAction(self.action_config)
        self.menu.addAction(self.action_quit)
        self.setContextMenu(self.menu)
        
    
    def do_config(self):
        if not self.config_window:
            self.config_window = ConfigDialog()
        res = self.config_window.exec_()
        if res == QtGui.QDialog.Accepted:
            #const QString & title, const QString & message, MessageIcon icon = Information, int millisecondsTimeoutHint = 10000 )
            self.showMessage(self.trUtf8("Aviso"),
                             self.trUtf8("Los cambios no tendrán efecto hasta que reinicie el servidor"),
                             QtGui.QSystemTrayIcon.Information, 2000)
    @property
    def port(self):
        # El puerto por defecto es 8080
        port, ok = self.config.value('server/port')
        return ok and port or 8080
    
    def do_quit(self):
        # Le pedimos a la instancia que se cierre
        QtGui.QApplication.instance().exit()
    
    def do_handle_activation(self, reason):
        if reason == QtGui.QSystemTrayIcon.DoubleClick:
            self.do_config()
    
    def on_opt_open_browser_toggled(self, val):
        ''' Acción del menú de iniciar automáticamente el browser
        con el servidor '''
        self.app.start_browser = val
        print "Ahora iniciar browser es", val
    
    @QtCore.pyqtSignature("")
    def on_opt_server_port_triggered(self):
        val, ok = \
        QtGui.QInputDialog.getInteger(None,
                                      self.trUtf8("Puerto del servidor web"),
                                      self.trUtf8("Puerto del servidor web"),
                                      self.app.port,1025,65535
                                      
                                      )
        if ok:
            self.app.port = val
            self.action_opt_server_port.setText("Puerto %d" % val)
    def started(self):
        self.action_start.setEnabled(False)
        self.action_restart.setEnabled(True)
        self.action_stop.setEnabled(True)
        #( const QString & title, const QString & message, MessageIcon icon = Information, int millisecondsTimeoutHint = 10000 )
        self.showMessage(self.trUtf8("Servidor iniciado"),
                         self.trUtf8("Servidor iniciado"),
                         self.Information,
                         2000)
        
    def stoped(self):
        self.action_start.setEnabled(True)
        self.action_restart.setEnabled(False)
        self.action_stop.setEnabled(False)
        self.showMessage(self.trUtf8("Servidor terminado"),
                         self.trUtf8("Servidor terminado"),
                         self.Information,
                         2000)
        
    @QtCore.pyqtSignature("char*")
    def aborted(self, reason):
        self.action_start.setEnabled(True)
        self.action_restart.setEnabled(False)
        self.action_stop.setEnabled(False)
        self.showMessage(self.trUtf8("Servidor abortado"),
                         self.trUtf8("El servidor ha sido abortado (%s)" % reason),
                         self.Information,
                         2000)
        
#===============================================================================
#    Sever control
#===============================================================================
    def start_server(self):
        self.server.server_start()
    def stop_server(self):
        self.server.server_stop()
    def restart_server(self):
        self.server.server_restart()