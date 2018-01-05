from Core.RedditObjects import Subreddit, User


class UserFinderUser(User):

    """
    A subclass of the User class used to hold information about a user for use by the UserFinder
    """

    def __init__(self, karma, version, name, save_path, post_limit, avoid_duplicates, download_videos, download_images,
                 nsfw_filter, name_downloads_by, user_added):
        super().__init__(version, name, save_path, post_limit, avoid_duplicates, download_videos, download_images,
                         nsfw_filter, name_downloads_by, user_added)
        self.total_karma = karma
        self.last_post_date = None

    @property
    def save_directory(self):
        """
        Overrides the super User class's save directory property to provide a text item that is not used but also does
        not cause exceptions in other parts of the program that need a text path here.
        :return: A mock path string
        :rtype: str
        """
        return 'path/'


class UserFinderSubreddit(Subreddit):

    """
    A subclass of the Subreddit class used to hold information about a subreddit for use by the UserFinder
    """

    def __init__(self, version, name, save_path, post_limit, avoid_duplicates, download_videos, download_images,
                 nsfw_filter, subreddit_save_method, name_downloads_by, user_added):
        super().__init__(version, name, save_path, post_limit, avoid_duplicates, download_videos, download_images,
                         nsfw_filter, subreddit_save_method, name_downloads_by, user_added)
        self.extracted_post_dict = {}

    def consolidate_posts(self):
        """
        Combs through posts in the new submissions list for posts that may have the same author, and if found
        consolidates the posts to the extracted_post_dict under the key of the authors name for easier use.
        """
        for post in self.new_submissions:
            if post.author.name in self.extracted_post_dict:
                self.extracted_post_dict[post.author.name].append(post)
            else:
                self.extracted_post_dict[post.author.name] = [post]
