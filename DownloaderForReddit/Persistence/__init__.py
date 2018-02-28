from Core import *
from Extractors import BaseExtractor
from Core import RedditObjects
import sys

sys.modules['RedditObjects'] = RedditObjects
sys.modules['BaseExtractor'] = BaseExtractor
