

class Post(object):
    def __init__(self, url, author, title, subreddit, created):
        """
        A class that holds information about a post made on reddit.  This class is used to save post information and
        is also used by the UserFinder.
        :param url: The url that the post links to.
        :param author: The user who made the post to reddit.
        :param title: The title of the post.
        :param subreddit: The subreddit in which the post was made.
        :param created: The epoch time that the post was made.
        """
        self.url = url
        self.author = author
        self.title = title
        self.subreddit = subreddit
        self.created = created
