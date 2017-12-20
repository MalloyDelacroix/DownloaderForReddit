from Core import *
from Extractors import Extractors
from Core import RedditObjects
import sys

sys.modules['RedditObjects'] = RedditObjects
sys.modules['Extractor'] = Extractors
