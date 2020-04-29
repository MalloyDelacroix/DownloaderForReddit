import traceback
from abc import ABC
from sqlalchemy.sql import func
from sqlalchemy import or_
from sqlalchemy import desc as descending

from .Models import RedditObjectList, RedditObject, DownloadSession, Post, Content, Comment, ListAssociation


class Filter(ABC):

    """
    An abstract class that filters database model queries based on a list of supplied tuples that correspond to model
    attributes.
    """

    op_map = {
        'eq': lambda attr, value: attr == value,
        'lt': lambda attr, value: or_(attr == None, attr < value),
        'lte': lambda attr, value: or_(attr == None, attr <= value),
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
        self.custom_filter_map = {}
        self.order_map = {}

    def filter(self, session, *filters, query=None, order_by=None, desc=False):
        self.session = session
        if query is None:
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
                traceback.print_exc()
        query = self.order_query(query, order_by, desc)
        return query

    def order_query(self, query, order, desc):
        if order is None:
            order = self.default_order
        order_by = getattr(self.model, order, None)
        if order_by is None:
            try:
                query, order_by = self.order_map[order](query)
            except KeyError:
                print('key error')
                order_by = self.default_order
        if desc:
            order_by = descending(order_by)
        return query.order_by(order_by)

    def custom_filter(self, query, attr, operator, value):
        try:
            return self.custom_filter_map[attr](query, operator, value)
        except KeyError:
            return query


class RedditObjectListFilter(Filter):

    model = RedditObjectList
    default_order = 'name'

    def __init__(self):
        super().__init__()
        self.custom_filter_map = {
            'reddit_object_count': self.filter_reddit_object_count,
            'total_score': self.filter_total_score,
        }

        self.order_map = {
            'reddit_object_count': self.order_by_reddit_object_count,
            'total_score': self.order_by_total_score,
        }

    def get_reddit_object_count_sub(self):
        return self.session.query(ListAssociation.reddit_object_list_id,
                                 func.count(ListAssociation.reddit_object_id).label('ro_count')) \
            .group_by(ListAssociation.reddit_object_list_id).subquery()

    def get_total_score_sub(self):
        return self.session.query(ListAssociation.reddit_object_list_id, Post.significant_reddit_object_id,
                                  func.sum(Post.score).label('total_score'))\
            .join(Post, Post.significant_reddit_object_id == ListAssociation.reddit_object_id)\
            .group_by(ListAssociation.reddit_object_list_id).subquery()

    def join_query(self, query, sub):
        return query.outerjoin(sub, RedditObjectList.id == sub.c.reddit_object_list_id)

    def filter_reddit_object_count(self, query, operator, value):
        sub = self.get_reddit_object_count_sub()
        f = self.op_map[operator](sub.c.ro_count, value)
        query = self.join_query(query, sub).filter(f)
        return query

    def filter_total_score(self, query, operator, value):
        sub = self.get_total_score_sub()
        f = self.op_map[operator](sub.c.total_score, value)
        query = self.join_query(query, sub).filter(f)
        return query

    def order_by_reddit_object_count(self, query):
        sub = self.get_reddit_object_count_sub()
        query = self.join_query(query, sub)
        return query, sub.c.ro_count

    def order_by_total_score(self, query):
        sub = self.get_total_score_sub()
        query = self.join_query(query, sub)
        return query, sub.c.total_score


class RedditObjectFilter(Filter):

    model = RedditObject
    default_order = 'name'

    def __init__(self):
        super().__init__()
        self.custom_filter_map = {
            'post_score': self.filter_post_score,
            'post_count': self.filter_post_count,
            'comment_score': self.filter_comment_score,
            'comment_count': self.filter_comment_count,
            'content_count': self.filter_content_count,
            'download_count': self.filter_download_count,
            'last_post_date': self.filter_last_post_date,
        }

        self.order_map = {
            'post_score': self.order_by_score,
            'post_count': self.order_by_post_count,
            'comment_score': self.order_by_comment_score,
            'comment_count': self.order_by_comment_count,
            'content_count': self.order_by_content_count,
            'download_count': self.order_by_download_count,
            'last_post_date': self.order_by_last_post_date,
        }

    def get_score_sum_sub(self):
        return self.session.query(Post.significant_reddit_object_id, func.sum(Post.score).label('total_score')) \
            .group_by(Post.significant_reddit_object_id).subquery()

    def get_post_count_sub(self):
        return self.session.query(Post.significant_reddit_object_id, func.count(Post.id).label('post_count'))\
            .group_by(Post.significant_reddit_object_id).subquery()

    def get_comment_score_sub(self):
        return self.session.query(Post.significant_reddit_object_id, func.sum(Comment.score).label('total_score'))\
            .join(Post).group_by(Post.significant_reddit_object_id).subquery()

    def get_comment_count_sub(self):
        return self.session.query(Post.significant_reddit_object_id, func.count(Comment.id).label('comment_count'))\
            .join(Post).group_by(Post.significant_reddit_object_id).subquery()

    def get_content_count_sub(self):
        return self.session.query(Post.significant_reddit_object_id, func.count(Content.id).label('content_count')) \
            .join(Post).group_by(Post.significant_reddit_object_id).subquery()

    def get_download_count_sub(self):
        return self.session.query(Post.significant_reddit_object_id,
                                  func.count(Post.download_session_id.distinct()).label('dl_count')) \
            .group_by(Post.significant_reddit_object_id).subquery()

    def get_last_post_date_sub(self):
        return self.session.query(Post.significant_reddit_object_id,
                                  func.max(Post.date_posted).label('last_post_date'))\
            .group_by(Post.significant_reddit_object_id).subquery()

    def join_queries(self, query, sub):
        return query.outerjoin(sub, RedditObject.id == sub.c.significant_reddit_object_id)

    def filter_post_score(self, query, operator, value):
        sub = self.get_score_sum_sub()
        f = self.op_map[operator](sub.c.total_score, value)
        query = self.join_queries(query, sub).filter(f)
        return query

    def filter_post_count(self, query, operator, value):
        sub = self.get_post_count_sub()
        f = self.op_map[operator](sub.c.post_count, value)
        query = self.join_queries(query, sub).filter(f)
        return query

    def filter_comment_score(self, query, operator, value):
        sub = self.get_comment_score_sub()
        f = self.op_map[operator](sub.c.total_score, value)
        query = self.join_queries(query, sub).filter(f)
        return query

    def filter_comment_count(self, query, operator, value):
        sub = self.get_comment_count_sub()
        f = self.op_map[operator](sub.c.comment_count, value)
        query = self.join_queries(query, sub).filter(f)
        return query

    def filter_content_count(self, query, operator, value):
        sub = self.get_content_count_sub()
        f = self.op_map[operator](sub.c.content_count, value)
        query = self.join_queries(query, sub).filter(f)
        return query

    def filter_download_count(self, query, operator, value):
        sub = self.get_download_count_sub()
        f = self.op_map[operator](sub.c.dl_count, value)
        query = self.join_queries(query, sub).filter(f)
        return query

    def filter_last_post_date(self, query, operator, value):
        sub = self.get_last_post_date_sub()
        f = self.op_map[operator](sub.c.last_post_date, value)
        query = self.join_queries(query, sub).filter(f)
        return query

    def order_by_score(self, query):
        sub = self.get_score_sum_sub()
        query = self.join_queries(query, sub)
        return query, sub.c.total_score

    def order_by_post_count(self, query):
        sub = self.get_post_count_sub()
        query = self.join_queries(query, sub)
        return query, sub.c.post_count

    def order_by_comment_score(self, query):
        sub = self.get_comment_score_sub()
        query = self.join_queries(query, sub)
        return query, sub.c.comment_score

    def order_by_comment_count(self, query):
        sub = self.get_comment_count_sub()
        query = self.join_queries(query, sub)
        return query, sub.c.comment_count

    def order_by_content_count(self, query):
        sub = self.get_content_count_sub()
        query = self.join_queries(query, sub)
        return query, sub.c.content_count

    def order_by_download_count(self, query):
        sub = self.get_download_count_sub()
        query = self.join_queries(query, sub)
        return query, sub.c.dl_count

    def order_by_last_post_date(self, query):
        sub = self.get_last_post_date_sub()
        query = self.join_queries(query, sub)
        return query, sub.c.last_post_date


class DownloadSessionFilter(Filter):

    model = DownloadSession
    default_order = 'id'

    def __init__(self):
        super().__init__()
        self.custom_filter_map = {
            'reddit_object_count': self.filter_reddit_object_count,
            'post_count': self.filter_post_count,
            'comment_count': self.filter_comment_count,
            'content_count': self.filter_content_count,
        }

        self.order_map = {
            'reddit_object_count': self.order_by_reddit_object_count,
            'post_count': self.order_by_post_count,
            'comment_count': self.order_by_comment_count,
            'content_count': self.order_by_content_count,
        }

    def get_reddit_object_count_sub(self):
        return self.session.query(Post.download_session_id,
                                 func.count(Post.significant_reddit_object_id.distinct()).label('ro_count'))\
            .group_by(Post.download_session_id).subquery()

    def get_post_count_sub(self):
        return self.session.query(Post.download_session_id, func.count(Post.id).label('post_count')) \
            .group_by(Post.download_session_id).subquery()

    def get_comment_count_sub(self):
        return self.session.query(Post.download_session_id, func.count(Comment.id).label('comment_count')) \
            .join(Post).group_by(Post.download_session_id).subquery()

    def get_content_count_sub(self):
        return self.session.query(Post.download_session_id, func.count(Content.id).label('content_count')) \
            .join(Post).group_by(Post.download_session_id).subquery()

    def join_queries(self, query, sub):
        return query.outerjoin(sub, DownloadSession.id == sub.c.download_session_id)

    def filter_reddit_object_count(self, query, operator, value):
        sub = self.get_reddit_object_count_sub()
        f = self.op_map[operator](sub.c.ro_count, value)
        query = self.join_queries(query, sub).filter(f)
        return query

    def filter_post_count(self, query, operator, value):
        sub = self.get_post_count_sub()
        f = self.op_map[operator](sub.c.post_count, value)
        query = self.join_queries(query, sub).filter(f)
        return query

    def filter_comment_count(self, query, operator, value):
        sub = self.get_comment_count_sub()
        f = self.op_map[operator](sub.c.comment_count, value)
        query = self.join_queries(query, sub).filter(f)
        return query

    def filter_content_count(self, query, operator, value):
        sub = self.get_content_count_sub()
        f = self.op_map[operator](sub.c.content_count, value)
        query = self.join_queries(query, sub).filter(f)
        return query

    def order_by_reddit_object_count(self, query):
        sub = self.get_reddit_object_count_sub()
        query = self.join_queries(query, sub)
        return query, sub.c.ro_count

    def order_by_post_count(self, query):
        sub = self.get_post_count_sub()
        query = self.join_queries(query, sub)
        return query, sub.c.post_count

    def order_by_comment_count(self, query):
        sub = self.get_comment_count_sub()
        query = self.join_queries(query, sub)
        return query, sub.c.comment_count

    def order_by_content_count(self, query):
        sub = self.get_content_count_sub()
        query = self.join_queries(query, sub)
        return query, sub.c.content_count


class PostFilter(Filter):

    model = Post
    default_order = 'title'

    def __init__(self):
        super().__init__()
        self.custom_filter_map = {
            'comment_count': self.comment_count_filter,
            'content_count': self.content_count_filter,
        }

    def get_comment_count_sub(self):
        return self.session.query(Comment.post_id, func.count(Comment.id).label('comment_count'))\
            .group_by(Comment.post_id).subquery()

    def get_content_count_sub(self):
        return self.session.query(Content.post_id, func.count(Content.id).label('content_count'))\
            .group_by(Content.post_id).subquery()

    def join_queries(self, query, sub):
        return query.outerjoin(sub, Post.id == sub.c.post_id)

    def comment_count_filter(self, query, operator, value):
        sub = self.get_comment_count_sub()
        f = self.op_map[operator](sub.c.comment_count, value)
        query = self.join_queries(query, sub).filter(f)
        return query

    def content_count_filter(self, query, operator, value):
        sub = self.get_content_count_sub()
        f = self.op_map[operator](sub.c.content_count, value)
        query = self.join_queries(query, sub).filter(f)
        return query

    def order_by_comment_count(self, query):
        sub = self.get_comment_count_sub()
        query = self.join_queries(query, sub)
        return query, sub.c.comment_count

    def order_by_content_count(self, query):
        sub = self.get_content_count_sub()
        query = self.join_queries(query, sub)
        return query, sub.c.content_count


class ContentFilter(Filter):

    model = Content
    default_order = 'title'

    def __init__(self):
        super().__init__()
        self.custom_filter_map = {
            'post_score': self.filter_post_score,
            'post_date': self.filter_date_posted,
            'nsfw': self.filter_nsfw,
            'domain': self.filter_domain,
        }

        self.order_map = {
            'post_score': self.order_by_post_score,
            'post_date': self.order_by_date_posted,
            'domain': self.order_by_domain,
        }

    def filter_post_score(self, query, operator, value):
        f = self.op_map[operator](Post.score, value)
        query = query.join(Post).filter(f)
        return query

    def filter_date_posted(self, query, operator, value):
        f = self.op_map[operator](Post.date_posted, value)
        query = query.join(Post).filter(f)
        return query

    def filter_nsfw(self, query, operator, value):
        f = self.op_map[operator](Post.nsfw, value)
        query = query.join(Post).filter(f)
        return query

    def filter_domain(self, query, operator, value):
        f = self.op_map[operator](Post.domain, value)
        query = query.join(Post).filter(f)
        return query

    def order_by_post_score(self, query):
        return query.join(Post), Post.score

    def order_by_date_posted(self, query):
        return query.join(Post), Post.date_posted

    def order_by_domain(self, query):
        return query.join(Post), Post.domain


class CommentFilter(Filter):

    model = Comment
    default_order = 'id'

    def __init__(self):
        super().__init__()
        self.custom_filter_map = {
            'post_score': self.post_score_filter,
            'post_date': self.post_date_filter,
            'nsfw': self.nsfw_filter,
        }

        self.order_map = {
            'post_score': self.order_by_post_score,
            'post_date': self.order_by_post_date,
        }

    def post_score_filter(self, query, operator, value):
        f = self.op_map[operator](Post.score, value)
        query = query.join(Post).filter(f)
        return query

    def post_date_filter(self, query, operator, value):
        f = self.op_map[operator](Post.date_posted, value)
        query = query.join(Post).filter(f)
        return query

    def nsfw_filter(self, query, operator, value):
        f = self.op_map[operator](Post.nsfw, value)
        query = query.join(Post).filter(f)
        return query

    def order_by_post_score(self, query):
        return query.join(Post), Post.score

    def order_by_post_date(self, query):
        return query.join(Post), Post.date_posted
