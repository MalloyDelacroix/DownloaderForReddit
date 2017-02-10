from setuptools import setup
from DownloaderForReddit.version import __version__

setup(
    name='DownloaderForReddit',
    version=__version__,
    packages=[''],
    url='https://github.com/MalloyDelacroix/DownloaderForReddit',
    license='GNU GPLv3',
    author='Kyle Hickey',
    author_email='kyle.hickey222@gmail.com',
    description='A GUI application with some advanced features that downloads user posted content from reddit, '
                'either via a list of users or subreddits.'
)
