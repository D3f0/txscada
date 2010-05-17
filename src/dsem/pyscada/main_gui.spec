# Analisis del script
a = Analysis([os.path.join(HOMEPATH,'support\\_mountzlib.py'), os.path.join(HOMEPATH,'support\\useUnicode.py'), 'main_gui.py'],
             pathex=['E:\\src\\dsem\\pyscada', 'E:\\src\\dsem\\', 'E:\\src\\dsem\\picnet', 'E:\\src\\'])
pyz = PYZ(a.pure)

# Binario normal
exe = EXE(pyz,
          a.scripts,  #+ [('v', '', 'OPTION')],
          exclude_binaries=1,
          name='buildmain_gui/avrak.exe',
          debug=False,
          strip=False,
          upx=False,
          console=False,
          icon = 'res\\icons\\avrak_icon.ico' )
          
coll = COLLECT( exe,
               a.binaries,
               strip=False,
               upx=False,
               name='distmain_gui')

# Binario de depuracion
pyz_debug = PYZ(a.pure)
exe_debug = EXE(pyz,
          a.scripts,  #+ [('v', '', 'OPTION')],
          exclude_binaries=1,
          name='buildmain_gui/avrak_dbg.exe',
          debug=False,
          strip=False,
          upx=False,
          console=True,
          icon = 'res\\icons\\avrak_icon.ico' )
          
coll_debug = COLLECT( exe_debug,
               a.binaries,
               strip=False,
               upx=False,
               name='distmain_gui')

# Instalador
a_installer = a = Analysis([os.path.join(HOMEPATH,'support\\_mountzlib.py'), os.path.join(HOMEPATH,'support\\useUnicode.py'), 
                    'win_setup.py'],)
pyz_installer = PYZ(a_installer.pure)

exe_installer = EXE(pyz_installer,
                a_installer.scripts,
                exclude_inaries=1,
                name='buildmain_gui/cfg_setup.exe',
                debug=False,
                strip=False,
                upx=False,
                console=True,)

coll_installer = COLLECT( exe_installer,
                          a_installer.binaries,
                          strip=False,
                          upx=False,
                          name='distmain_gui')
                
                
