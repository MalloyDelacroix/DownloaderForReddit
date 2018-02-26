from Core import *
from Extractors import Extractor
from Core import RedditObjects
import sys

sys.modules['RedditObjects'] = RedditObjects
sys.modules['Extractor'] = Extractor
