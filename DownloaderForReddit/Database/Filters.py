from abc import ABC
from sqlalchemy.sql import func

from .DatabaseHandler import DatabaseHandler
from .Models import RedditObjectList, RedditObject, DownloadSession, Post, Content, Comment


class Filter(ABC):

    """
    An abstract class that filters database model queries based on a list of supplied tuples that correspond to model
    attributes.
    """

    metadata = DatabaseHandler.base.metadata
    model = None
    default_order = 'id'

    @classmethod
    def query(cls, session, filters, order_by=None):
        """
        Filters this class's model class based on the tuples provided in the supplied filters list.  If order_by is not
        supplied, the query is ordered by the class's default_order identifier.
        :param session: The session that will be used to query the database.
        :param filters: A list of tuples used to filter the model class.  The tuple order should be: (model_attribute,
                        filter_expression_operator, filtered_value)
        :param order_by: The model attribute that should be used to filter the query.
        :return: A query of the class's model class filtered by the supplied filters list.
        """
        query = session.query(cls.model)
        for tup in filters:
            key, op, value = tup
            col = getattr(cls.model, key, None)
            if not col:
                print('no column')
                return None
            if op == 'in':
                if isinstance(value, list):
                    f = col.in_(value)
                else:
                    f = col.in_(value.split(','))
            else:
                try:
                    attr = list(filter(lambda e: hasattr(col, e % op), ['%s', '%s_', '__%s__']))[0] % op
                except IndexError:
                    print('attribute index error')
                    return None
                if value == 'null':
                    value = None
                f = getattr(col, attr)(value)
                print(f)
            query = query.filter(f)

        if order_by is None:
            order_by = cls.default_order
        return query.order_by(order_by)


class RedditObjectListFilter(Filter):

    model = RedditObjectList
    default_order = 'name'


class RedditObjectFilter(Filter):

    model = RedditObject
    default_order = 'name'

    # custom_queries = {
    #     'score': lambda op, value:
    # }
    #

    @classmethod
    def score_filter(cls, session, query, operator, value):
        scores = session.query(func.sum(Post.score)).label('score').group_by(Post.significant_reddit_object_id).subquery()
        query = query.filter(getattr(cls.model, 'score')(value))


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
