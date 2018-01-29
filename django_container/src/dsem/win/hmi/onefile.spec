a = Analysis([os.path.join(HOMEPATH,'support\\_mountzlib.py'), os.path.join(HOMEPATH,'support\\useUnicode.py'), 'main.py'],
             pathex=['C:\\src\\dsem\\win\\hmi'])
pyz = PYZ(a.pure)
exe = EXE( pyz,
          a.scripts,
          a.binaries,
          name='main.exe',
          debug=False,
          strip=False,
          upx=False,
          console=False )
