a = Analysis([os.path.join(HOMEPATH,'support\\_mountzlib.py'), os.path.join(HOMEPATH,'support\\useUnicode.py'), 'main.py'],
             pathex=['C:\\src\\dsem\\win\\hmi'])
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name='buildmain/main.exe',
          debug=False,
          strip=False,
          upx=False,
          console=False )
coll = COLLECT( exe,
               a.binaries,
               strip=False,
               upx=False,
               name='distmain')
