import praw

from version import __version__


reddit_instance = None


def get_reddit_instance():
    global reddit_instance
    if not reddit_instance:
        reddit_instance = praw.Reddit(user_agent='python:DownloaderForReddit:%s (by /u/MalloyDelacroix)' % __version__,
                              client_id='frGEUVAuHGL2PQ', client_secret=None)
    return reddit_instance
