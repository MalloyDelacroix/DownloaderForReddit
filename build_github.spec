# -*- mode: python -*-
import os
import sys

# work-around for https://github.com/pyinstaller/pyinstaller/issues/4064
# import distutils
# print(distutils.__file__)
# if distutils.distutils_path.endswith('__init__.py'):
#     distutils.distutils_path = os.path.dirname(distutils.distutils_path)


block_cipher = None

dir_path = os.path.abspath(SPECPATH)

import praw
praw_path = os.path.dirname(praw.__file__)
print(praw_path)
root = os.path.abspath(os.path.join(praw_path, os.pardir))
print(root)
python_folder = os.path.dirname(sys.executable)
print(python_folder)
import PyQt5


added_files = [(dir_path + '/Resources/images/*', 'Resources/images'),
			   (os.path.join(praw_path,'praw.ini'), '.'),
			   (dir_path + '/README.md', '.'), 
			   (dir_path + '/LICENSE', '.'), 
			   (dir_path + '/alembic', 'alembic'),
			   (dir_path + '/alembic/versions', 'alembic/versions'),
			   (dir_path + '/Resources/supported_video_sites.txt', 'Resources')]
print(added_files)

a = Analysis([dir_path + '/main.py'],
			 pathex=[python_folder, 
			 		root,
					root + '/PyQt5/Qt/bin',
					dir_path],
			 binaries=[],
			 datas=added_files,
			 hiddenimports=['resource', 'pkg_resources.py2_warn', 'sqlalchemy.ext.baked'],
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
		  icon= dir_path + '/Resources/images/RedditDownloaderIcon_48x48.ico')
coll = COLLECT(exe,
			   a.binaries,
			   a.zipfiles,
			   a.datas,
			   strip=False,
			   upx=True,
			   name='DownloaderForReddit')
