import re
from operator import attrgetter


class TokenParser:

    regex = '%\[(.*?)\]'

    token_dict = {
        'title': lambda x: TokenParser.tokenize(x, 'title', 'post.title'),
        'short_title': lambda x: TokenParser.tokenize(x, 'short_title', 'post.short_title'),
        'author_id': lambda x: TokenParser.tokenize(x, 'author.id', 'user.id'),
        'author_name': lambda x: TokenParser.tokenize(x, 'author.name', 'user.name'),
        'author_reddit_id': lambda x: TokenParser.tokenize(x, 'author.reddit_id', 'user.reddit_id'),
        'subreddit_id': lambda x: TokenParser.tokenize(x, 'subreddit.id'),
        'subreddit_name': lambda x: TokenParser.tokenize(x, 'subreddit.name'),
        'subreddit_reddit_id': lambda x: TokenParser.tokenize(x, 'subreddit.reddit_id'),
        'post_id': lambda x: TokenParser.tokenize(x, 'post.id', 'id'),
        'post_title': lambda x: TokenParser.tokenize(x, 'post.title', 'title'),
        'post_short_title': lambda x:TokenParser.tokenize(x, 'post.short_title', 'short_title'),
        'post_author_name': lambda x: TokenParser.tokenize(x, 'post.author.name', 'author.name'),
        'post_author_id': lambda x: TokenParser.tokenize(x, 'post.author.id', 'author.id'),
        'post_subreddit_name': lambda x: TokenParser.tokenize(x, 'post.subreddit.name', 'subreddit.name'),
        'post_subreddit_id': lambda x: TokenParser.tokenize(x, 'post.subreddit.id', 'subreddit.id'),
        'post_domain': lambda x: TokenParser.tokenize(x, 'post.domain', 'domain'),
        'date_posted': lambda x: TokenParser.tokenize(x, 'post.date_posted', 'date_posted'),
        'extraction_date': lambda x: TokenParser.tokenize(x, 'post.extraction_date', 'extraction_date'),
        'download_date': lambda x: TokenParser.tokenize(x, 'download_date', 'post.download_date'),
        'id': lambda x: TokenParser.tokenize(x, 'id', 'post.id', 'author.id', 'user.id', 'subreddit.id',
                                             'reddit_object.id')
    }

    @classmethod
    def parse_tokens(cls, obj, string):
        """
        Parses a token string and replaces the tokens with the values that they should represent from the supplied
        object.
        :param obj: The database model who's attributes the tokens in the token string should represent.
        :param string: A string with tokens that are to be replaced with values from the supplied object.
        """
        matches = re.findall(cls.regex, string)
        for match in matches:
            attr_token = cls.token_dict.get(match, None)
            if attr_token is not None:
                string = string.replace(f'%[{match}]', attr_token(obj))
        return string

    @classmethod
    def tokenize(cls, obj, *args, index=0):
        """
        A recursive method that attempts to retrieve the object attribute represented by the string in args at the
        supplied index.  If the supplied object does not have a matching attribute, the index is increased and the
        method called recursively.  Returns an empty string if there are no matching attributes supplied.
        :param obj: The object who's attributes are to be retrieved.
        :param args: A list of attribute strings that attrgetter can use to pull values from the supplied object.
        :param index: The position in args that should be used this iteration.
        :return: An attribute from the supplied object that matches the attribute string from args at the supplied
                 index.  Will be an empty string if there are no matches.
        """
        try:
            return str(attrgetter(args[index])(obj))
        except AttributeError:
            return cls.tokenize(obj, index=index + 1, *args)
        except IndexError:
            return ''
