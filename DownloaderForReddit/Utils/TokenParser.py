import re
from operator import attrgetter


class TokenParser:

    regex = '%\[(.*?)\]'

    token_dict = {
        'author_id': lambda x: TokenParser.tokenize(x, 'author.id', 'user.id'),
        'author_name': lambda x: TokenParser.tokenize(x, 'author.name', 'user.name'),
        'author_reddit_id': lambda x: TokenParser.tokenize(x, 'author.reddit_id', 'user.reddit_id'),
        'subreddit_id': lambda x: TokenParser.tokenize(x, 'subreddit.id'),
        'subreddit_name': lambda x: TokenParser.tokenize(x, 'subreddit.name'),
        'subreddit_reddit_id': lambda x: TokenParser.tokenize(x, 'subreddit.reddit_id'),
        'post_id': lambda x: TokenParser.tokenize(x, 'post.id', 'id'),
        'post_domain': lambda x: TokenParser.tokenize(x, 'post.domain', 'domain'),
        'date_posted': lambda x: TokenParser.tokenize(x, 'post.date_posted', 'date_posted'),
        'extraction_date': lambda x: TokenParser.tokenize(x, 'post.extraction_date', 'extraction_date'),
        'title': lambda x: TokenParser.tokenize(x, 'title', 'post.title'),
        'download_date': lambda x: TokenParser.tokenize(x, 'download_date'),
        'id': lambda x: TokenParser.tokenize(x, 'id', 'post.id', 'author.id', 'user.id', 'subreddit.id',
                                             'reddit_object.id')
    }

    @classmethod
    def parse_tokens(cls, obj, string):
        matches = re.findall(cls.regex, string)
        for match in matches:
            attr_token = cls.token_dict.get(match, None)
            if attr_token is not None:
                string = string.replace(f'%[{match}]', attr_token(obj))
        return string

    @classmethod
    def tokenize(cls, obj, *args, index=0):
        try:
            return str(attrgetter(args[index])(obj))
        except AttributeError:
            return cls.tokenize(obj, index=index + 1, *args)
        except IndexError:
            return ''
