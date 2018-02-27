from Extractors.ImgurExtractor import ImgurExtractor
from Extractors.GfycatExtractor import GfycatExtractor
from Extractors.VidbleExtractor import VidbleExtractor
from Extractors.RedditUploadsExtractor import RedditUploadsExtractor
from Extractors.DirectExtractor import DirectExtractor


class ExtractorConfig:

    extractor_dict = {
        'imgur': ImgurExtractor,
        'gfycat': GfycatExtractor,
        'vidble': VidbleExtractor,
        'redd.it': RedditUploadsExtractor,
    }

    def __init__(self, reddit_object):
        """
        Makes an instance of the ExtractorConfig which is used to assign an extractor based on the hosting website of
        a post url and then take the necessary actions to extract the content from the website.
        :param reddit_object: The reddit object for which contains lists of posts to be extracted.
        :type reddit_object: RedditObject
        """
        self.reddit_object = reddit_object

    def run(self):
        for post in self.reddit_object.saved_submissions:
            pass
        for post in self.reddit_object.new_submissions:
            pass

    def extract(self, post):
        subreddit = self.get_subreddit(post)
        try:
            extractor = self.assign_extractor(post)(post.url, post.author, post.title, subreddit, post.created,
                                                    self.reddit_object.subreddit_save_method,
                                                    self.reddit_object.name_downloads_by,
                                                    self.reddit_object.save_directory,
                                                    self.reddit_object.content_display_only)
            # TODO: Finish setting this up to extract content, also needs to check dates and duplicate, image, video filter
        except TypeError:
            self.reddit_object.failed_extracts.append('Could not extract from post: Url domain not supported\n'
                                                      'Url: %s, User: %s, Subreddit: %s, Title: %s' %
                                                      (post.url, post.user, post.subreddit, post.title))
            # TODO Log this

    def get_subreddit(self, post):
        """
        Method returns the subreddit the post was submitted in if the reddit object type is not subreddit, otherwise
        the reddit objects name is used.  This is done so that folder names for subreddit downloads match the user
        entered subreddit names capitalization wise.  If this is not used subreddit download folders capitalization may
        not match the subreddit object in the list and therefore the downloaded content view may not work correctly.
        :param post: The post taken from reddit.
        :type post: praw.Post
        :return: The name of the subreddit as it is to be used in the download process.
        :rtype: str
        """
        return post.subreddit if self.reddit_object.object_type != 'SUBREDDIT' else self.reddit_object.name

    def assign_extractor(self, post):
        for key, value in self.extractor_dict.items():
            if key in post.url:
                return value
        if post.url.lower().endswith(DirectExtractor.extensions):
            return DirectExtractor
        return None
