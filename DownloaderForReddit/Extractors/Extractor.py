import logging

from Extractors.BaseExtractor import BaseExtractor
from Extractors.DirectExtractor import DirectExtractor
from Core import Injector
from Core import Const


class Extractor:

    def __init__(self, reddit_object):
        """
        Makes an instance of the Extractor which is used to assign an extractor based on the hosting website of
        a post url and then take the necessary actions to extract the content from the website.
        :param reddit_object: The reddit object for which contains lists of posts to be extracted.
        :type reddit_object: RedditObject
        """
        self.settings_manager = Injector.get_settings_manager()
        self.logger = logging.getLogger('DownloaderForReddit.%s' % __name__)
        self.reddit_object = reddit_object

    def run(self):
        for post in self.reddit_object.saved_submissions:
            self.extract(post)
        for post in self.reddit_object.new_submissions:
            self.extract(post)

    def extract(self, post):
        self.reddit_object.set_date_limit(post.created)
        try:
            extractor = self.assign_extractor(post)(post, self.reddit_object)
            extractor.extract_content()
            self.handle_content(extractor)
        except TypeError:
            print('Failed Url: %s' % post.url)
            self.reddit_object.failed_extracts.append('Could not extract from post: Url domain not supported\n'
                                                      'Url: %s, User: %s, Subreddit: %s, Title: %s' %
                                                      (post.url, post.author, post.subreddit, post.title))
            self.logger.error('Failed to find extractor for domain', extra={'url': post.url,
                                                                            'reddit_object': self.reddit_object.json})

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

    # TODO: Need to thoroughly test this new method of extractor assignment
    def assign_extractor(self, post):
        """
        Selects and returns the extractor to be used based on the url of the supplied post.
        :param post: The post that is to be extracted.
        :type post: praw.Post
        :return: The extractor that is to be used to extract content from the supplied post.
        :rtype: BaseExtractor
        """
        for extractor in BaseExtractor.__subclasses__():
            if extractor.get_url_key() in post.url.lower():
                return extractor
        if post.url.lowr().endswith(DirectExtractor.extensions):
            return DirectExtractor
        return None

    def handle_content(self, extractor):
        """
        Takes the appropriate action for content that was extracted or failed to extract.
        :param extractor: The extractor that contains the extracted content.
        :type extractor: BaseExtractor
        """
        self.save_submissions(extractor)
        for x in extractor.failed_extract_messages:
            self.reddit_object.failed_extracts.append(x)
        for content in extractor.extracted_content:
            if type(content) == str and content.startswith('Failed'):
                self.reddit_object.failed_extracts.append(content)
            else:
                if self.filter_content(content):
                    self.reddit_object.content.append(content)
                    self.reddit_object.previous_downloads.append(content.url)

    def save_submissions(self, extractor):
        """
        Saves any content that need to be saved.  A check is performed to make sure the content is not already in the
        saved list.
        :param extractor: The extractor that contains the content to be saved.
        :type extractor: BaseExtractor
        """
        for x in extractor.failed_extracts_to_save:
            if not any(x.url == y.url for y in self.reddit_object.saved_submissions):
                self.reddit_object.saved_submissions.append(x)

    def filter_content(self, content):
        """
        Checks the various content filters to see if the supplied content meets the filter standards.
        :param content: The content that is to be filtered.
        :type content: Content
        :return: True or false depending on if the content passes or fails the filter.
        :rtype: bool
        """
        return self.check_image(content) and self.check_video(content) and self.check_duplicate(content)

    def check_image(self, content):
        return self.reddit_object.download_images or not content.endswith(Const.IMAGE_EXT)

    def check_video(self, content):
        return self.reddit_object.download_videos or not content.endswith(Const.VID_EXT)

    def check_duplicate(self, content):
        return not self.reddit_object.avoid_duplicates or content.url not in self.reddit_object.previous_downloads
