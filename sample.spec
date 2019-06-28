# -*- mode: python -*-

block_cipher = None

dir_path = os.path.abspath(SPECPATH)
venv_path = '<path-to-virtual-env>'


added_files = [(dir_path + '/Resources/Images/*', 'Resources/Images'),
			   (venv_path + '/Lib/site-packages/praw/praw.ini', '.'),
			   (dir_path + '/README.md', '.'), 
			   (dir_path + '/LICENSE', '.'), 
			   (dir_path + '/The Downloader For Reddit - User Manual.pdf', '.'),
			   (dir_path + '/Resources/supported_video_sites.txt', 'Resources')]

a = Analysis([dir_path + '/main.py'],
			 pathex=[venv_path + '/Scripts', 
					 venv_path + '/Lib/site-packages/PyQt5/Qt/bin',
					 venv_path + '/Lib/site-packages',
					 dir_path],
			 binaries=[],
			 datas=added_files,
			 hiddenimports=['resource'],
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
		  icon= dir_path + '/Resources/Images/RedditDownloaderIcon_48x48.ico')
coll = COLLECT(exe,
			   a.binaries,
			   a.zipfiles,
			   a.datas,
			   strip=False,
			   upx=True,
			   name='DownloaderForReddit')
