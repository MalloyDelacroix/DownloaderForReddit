from abc import ABC
from sqlalchemy.sql import func
from sqlalchemy import desc as descending

from .DatabaseHandler import DatabaseHandler
from .Models import RedditObjectList, RedditObject, DownloadSession, Post, Content, Comment


class Filter(ABC):

    """
    An abstract class that filters database model queries based on a list of supplied tuples that correspond to model
    attributes.
    """

    op_map = {
        'eq': lambda attr, value: attr == value,
        'lt': lambda attr, value: attr < value,
        'lte': lambda attr, value: attr <= value,
        'gt': lambda attr, value: attr > value,
        'gte': lambda attr, value: attr >= value,
        'in': lambda attr, value: attr.in_(value),
        'like': lambda attr, value: attr.like(value),
        'wild_like': lambda attr, value: attr.like(f'%{value}%'),
        'contains': lambda attr, value: attr.contains(value)
    }

    model = None
    default_order = 'id'

    session = None

    def __init__(self):
        self.custom_filter_dict = {}

    def filter(self, session, filters, order_by=None, desc=False):
        self.session = session
        query = session.query(self.model)
        for tup in filters:
            key, operator, value = tup
            attr = getattr(self.model, key, None)
            if not attr:
                query = self.custom_filter(query, key, operator, value)
                continue
            if operator == 'in':
                if not isinstance(value, list):
                    value = value.split(',')
            try:
                f = self.op_map[operator](attr, value)
                query = query.filter(f)
            except Exception as e:
                print(e)
        if order_by is None:
            order_by = self.default_order
        if desc:
            order_by = descending(order_by)
        return query.order_by(order_by)

    def custom_filter(self, query, attr, operator, value):
        try:
            return self.custom_filter_dict[attr](query, operator, value)
        except KeyError:
            return query


class RedditObjectListFilter(Filter):

    model = RedditObjectList
    default_order = 'name'


class RedditObjectFilter(Filter):

    model = RedditObject
    default_order = 'name'

    def __init__(self):
        super().__init__()
        self.custom_filter_dict = {
            'score': self.post_score_filter,
            'post_count': self.post_count_filter,
            'content_count': self.content_count_filter,
            'comment_count': self.comment_count_filter,
        }

    def post_score_filter(self, query, operator, value):
        posts = self.session.query(Post.significant_reddit_object_id, func.sum(Post.score).label('total_score'))\
            .group_by(Post.significant_reddit_object_id).subquery()
        f = self.op_map[operator](posts.c.total_score, value)

        query = query.outerjoin(posts, RedditObject.id == posts.c.significant_reddit_object_id).filter(f)
        return query

    def post_count_filter(self, query, operator, value):
        posts = self.session.query(Post.significant_reddit_object_id, func.count(Post.id).label('post_count'))\
            .group_by(Post.significant_reddit_object_id).subquery()
        f = self.op_map[operator](posts.c.post_count, value)
        query = query.outerjoin(posts, RedditObject.id == posts.c.significant_reddit_object_id).filter(f)
        return query

    def content_count_filter(self, query, operator, value):
        content = self.session.query(Post.significant_reddit_object_id, func.count(Content.id).label('content_count'))\
            .join(Post).group_by(Post.significant_reddit_object_id).subquery()
        f = self.op_map[operator](content.c.content_count, value)
        query = query.outerjoin(content, RedditObject.id == content.c.significant_reddit_object_id).filter(f)
        return query

    def comment_count_filter(self, query, operator, value):
        comments = self.session.query(Post.significant_reddit_object_id, func.count(Comment.id).label('comment_count'))\
            .join(Post).group_by(Post.significant_reddit_object_id).subquery()
        f = self.op_map[operator](comments.c.comment_count, value)
        query = query.outerjoin(comments, RedditObject.id == comments.c.significant_reddit_object_id).filter(f)
        return query


class DownloadSessionFilter(Filter):

    model = DownloadSession
    default_order = 'id'


class PostFilter(Filter):

    model = Post
    default_order = 'title'


class ContentFilter(Filter):

    model = Content
    default_order = 'title'


class CommentFilter(Filter):

    model = Comment
    default_order = 'id'
