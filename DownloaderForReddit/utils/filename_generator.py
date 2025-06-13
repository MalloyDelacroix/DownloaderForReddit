from typing import Optional, Union

from . import injector, TokenParser, system_util
from ..database.models import Post, Content, Comment


class FilenameGenerator:

    """
    Provides functionality to generate filenames and directory paths based on given Reddit objects, handling duplicates,
    custom save paths, and naming methods.

    This class initializes and sets up the appropriate Reddit object, including posts and comments. It constructs
    title-based tokens and safely generates file paths by considering naming conventions, custom save paths, and save
    structures.

    :ivar settings_manager: The settings manager instance used to get configuration details for saving directories.
    :type settings_manager: SettingsManager
    :ivar post: The associated post object, extracted from the provided object.
    :type post: Post
    :ivar reddit_object: The significant Reddit object belonging to the post.
    :type reddit_object: RedditObject
    :ivar comment: The associated comment object, if applicable.
    :type comment: Comment
    :ivar is_duplicate: Flag indicating whether the object is a duplicate.
    :type is_duplicate: bool
    """

    def __init__(self, obj: Union[Post, Content, Comment], is_duplicate: bool = False):
        self.settings_manager = injector.get_settings_manager()
        self.post = None
        self.reddit_object = None
        self.comment = None
        self.is_duplicate = is_duplicate
        self.setup(obj)

    def setup(self, obj: Union[Post, Content, Comment]) -> None:
        """
        Configures internal state based on the provided object type. It handles several types of input objects and
        sets the corresponding attributes such as post, comment, and reddit_object.

        :param obj: The object to be used for configuration. It can be an instance of Comment, Content, or other types
                    containing a 'post' or 'significant_reddit_object' attribute.
        :type obj: Union[Comment, Content, Any]
        """
        if isinstance(obj, Comment):
            self.comment = obj
            self.post = obj.post
            self.reddit_object = self.post.significant_reddit_object
        elif isinstance(obj, Content):
            self.post = obj.post
            self.reddit_object = self.post.significant_reddit_object
            self.comment = None
        else:
            self.post = obj
            self.reddit_object = obj.significant_reddit_object
            self.comment = None

    @property
    def title_obj(self) -> Union[Post, Comment]:
        """
        Provides a property to return either a post or comment object, depending on which one is set.

        :return: Returns the `comment` object if it is not None; otherwise, returns the `post` object.
        :rtype: Union[Post, Comment]
        """
        if self.comment is not None:
            return self.comment
        else:
            return self.post

    def make_title(self) -> str:
        """
        Generate a title string by parsing tokens from the title object with the relevant data.

        :return: Parsed title string resulting from token processing
        """
        token_string = self._get_name_token_string()
        return TokenParser.parse_tokens(self.title_obj, token_string)

    def _get_name_token_string(self) -> str:
        """
        Constructs and returns a token string indicating the naming method of the Reddit object's associated entity.

        The naming method is determined by inspecting the object attributes. If a comment is associated, the naming
        corresponds to a comment-specific method. If the object is flagged as a duplicate, the naming is adjusted
        accordingly. Finally, a default naming method is used in all other cases.

        :return: A token string for the naming method based on the properties of the Reddit object
        """
        if self.comment is not None:
            return self.reddit_object.comment_naming_method
        elif self.is_duplicate:
            return self.reddit_object.duplicate_naming_method
        else:
            return self.reddit_object.post_download_naming_method

    def make_dir_path(self):
        """
        Generates a cleaned and correctly formatted directory path by combining base path and sub path constructed
        from tokens and object attributes.

        :return: A cleaned string representing the full directory path, ensuring it ends as a directory path.
        """
        token_string = self._get_dir_token_string()
        sub_path = TokenParser.parse_tokens(self.title_obj, token_string)
        clean_sub_path = system_util.clean_path(sub_path, ends_with_dir=True)
        base_path = self._get_base_path()
        combined_path = system_util.join_path(base_path, clean_sub_path)
        return combined_path

    def _get_dir_token_string(self) -> str:
        """
        Returns the token string used to generate the directory path based on what type title object is being used.

        It is possible for title objects to also be duplicates, which should take precedence.  `is_duplicate` is
        considered first, followed by comment, then the result defaults to the post save structure.
        :return: The token string used to generate the directory path for the title object.
        """
        if self.is_duplicate:
            return self.reddit_object.duplicate_save_structure
        elif self.comment is not None:
            return self.reddit_object.comment_save_structure
        else:
            return self.reddit_object.post_save_structure

    def _get_base_path(self) -> str:
        """
        Determine the base path to be used for saving operations.

        This method determines the base path by checking if there is a custom path set. If a custom path is provided,
        it will use that; otherwise, it defaults to returning a path based on the Reddit object type (e.g., user or
        subreddit) and the relevant global SettingsManager settings.

        :returns: The appropriate base path for saving files as a string.
        """
        custom_path = self._get_custom_path()
        if custom_path is not None and custom_path != '':
            return custom_path
        else:
            if self.reddit_object.object_type == 'USER':
                return self.settings_manager.user_save_directory
            else:
                return self.settings_manager.subreddit_save_directory

    def _get_custom_path(self) -> Optional[str]:
        """
        Returns the custom path to be used based on if the class has a comment set or not.
        :return: The custom path to be used, if one exists, or None.
        """
        if self.comment is not None:
            return self.reddit_object.custom_comment_save_path
        else:
            return self.reddit_object.custom_post_save_path
