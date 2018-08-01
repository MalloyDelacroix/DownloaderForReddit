import praw
import prawcore
from PyQt5.QtCore import QObject, pyqtSignal
import logging

from Core.Post import Post
from version import __version__


reddit_instance = None


def get_reddit_instance():
    global reddit_instance
    if not reddit_instance:
        reddit_instance = praw.Reddit(user_agent='python:DownloaderForReddit:%s (by /u/MalloyDelacroix)' % __version__,
                                      client_id='frGEUVAuHGL2PQ', client_secret=None)
    return reddit_instance


def convert_praw_post(praw_post):
    """
    A utility function that converts a praw submission object into a Post object which can be marshaled.  The method
    first checks to make sure that the supplied post is an instance of a praw submission object.
    """
    if isinstance(praw_post, praw.models.reddit.submission.Submission):
        return Post(praw_post.url, praw_post.author.name, praw_post.title, praw_post.subreddit.display_name,
                    praw_post.created, domain=praw_post.domain)
    else:
        return praw_post


class NameChecker(QObject):

    """
    This class is to check for the existence of a reddit object name using praw, then report back whether the name
    exists or not.  This class is intended to be ran in a separate thread.
    """

    name_validation = pyqtSignal(tuple)
    finished = pyqtSignal()

    def __init__(self, object_type, queue):
        """
        Initializes the NameChecker and establishes its operation setup regarding whether to target users or subreddits.
        :param object_type: The type of reddit object (USER or SUBREDDIT) that the supplied names will be.
        :param queue: The queue established by the caller in which names to be checked will be deposited.
        :type object_type: str
        :type queue: Queue
        """
        super().__init__()
        self.logger = logging.getLogger('DownloaderForReddit.%s' % __name__)
        self.r = get_reddit_instance()
        self.continue_run = True
        self.object_type = object_type
        self.queue = queue

    def run(self):
        """
        Continuously checks the queue for a new name then calls the check name method when one is extracted from the
        queue.  Responsible for emitting the finished signal when the class is done and is to be destroyed.
        """
        while self.continue_run:
            name = self.queue.get()
            if name is not None:
                self.check_name(name)
        self.finished.emit()

    def stop_run(self):
        """
        Switches off the run cycle.  None is added to the queue because the run method will block until it receives
        something from the queue.
        """
        self.continue_run = False
        self.queue.put(None)

    def check_name(self, name):
        if self.object_type == 'USER':
            self.check_user_name(name)
        else:
            self.check_subreddit_name(name)

    def check_user_name(self, name):
        user = self.r.redditor(name)
        try:
            test = user.fullname
            self.name_validation.emit((name, True))
        except (prawcore.exceptions.NotFound, prawcore.exceptions.Redirect, AttributeError):
            self.name_validation.emit((name, False))
        except:
            self.logger.error('Unable to validate user name', extra={'user_name': name}, exc_info=True)

    def check_subreddit_name(self, name):
        sub = self.r.subreddit(name)
        try:
            test = sub.fullname
            self.name_validation.emit((name, True))
        except (prawcore.exceptions.NotFound, prawcore.exceptions.Redirect, AttributeError):
            self.name_validation.emit((name, False))
        except:
            self.logger.error('Unable to validate subreddit name', extra={'subreddit_name': name}, exc_info=True)
