from time import time


# A dict for keeping track of timeout times for each extractor
time_limit_dict = {}
timeout_dict = {}


def set_timeout(extractor):
    timeout_dict[type(extractor).__name__] = time()
