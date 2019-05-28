# -*- mode: python -*-

block_cipher = None

added_files = [('<path-to-project-directory>/Resources/Images/*', 'Resources/Images'),
			   ('<path-to-virtual-env>/Lib/site-packages/praw/praw.ini', '.'),
			   ('<path-to-project-directory>/README.md', '.'), 
			   ('<path-to-project-directory>/LICENSE', '.'), 
			   ('<path-to-project-directory>/The Downloader For Reddit - User Manual.pdf', '.'),
			   ('<path-to-project-directory>/Resources/supported_video_sites.txt', 'Resources')]

a = Analysis(['<path-to-project-directory>/main.py'],
             pathex=['<path-to-virtual-env>/Scripts', 
					 '<path-to-virtual-env>/Lib/site-packages/PyQt5/Qt/bin',
					 '<path-to-virtual-env>/Lib/site-packages',
					 '<path-to-project-directory>'],
             binaries=[],
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='DownloaderForReddit',
          debug=False,
          strip=False,
          upx=True,
          console=False, 
		  icon='<path-to-project-directory>/Resources/Images/RedditDownloaderIcon_48x48.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='DownloaderForReddit')
