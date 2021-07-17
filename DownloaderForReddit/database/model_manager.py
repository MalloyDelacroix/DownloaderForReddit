import math

from ..utils import injector, system_util
from .models import Post, Content, Comment, ListAssociation


def check_session(method):
    def check(*args, **kwargs):
        if kwargs.get('session', None) is None:
            with injector.get_database_handler().get_scoped_session() as session:
                kwargs['session'] = session
                return method(*args, **kwargs)
        return method(*args, **kwargs)

    return check


class ModelManger:

    """
    Manages the deletion of database objects and their related models and respective files.
    """

    @classmethod
    @check_session
    def delete_list(cls, ro_list, session=None, cascade=False):
        if cascade:
            for ro in ro_list.reddit_objects:
                cls.delete_reddit_object(ro, session=session)
        session.delete(ro_list)
        session.commit()

    @classmethod
    @check_session
    def delete_reddit_object(cls, reddit_object, session=None, delete_files=False):
        post_ids = session.query(Post.id).filter(Post.significant_reddit_object_id == reddit_object.id)
        comment_ids = session.query(Comment.id).filter(Comment.post_id.in_(post_ids))
        cls.bulk_delete(Comment, session, comment_ids)
        files = []
        if delete_files:
            content = session.query(Content).filter(Content.post_id.in_(post_ids))
            files = [c.get_full_file_path() for c in content]
        content_ids = session.query(Content.id).filter(Content.post_id.in_(post_ids))
        cls.bulk_delete(Content, session, content_ids)
        cls.bulk_delete(Post, session, post_ids)
        session.query(ListAssociation).filter(ListAssociation.reddit_object_id == reddit_object.id).delete()
        session.delete(reddit_object)
        session.commit()
        for file in files:
            system_util.delete_file(file)

    @classmethod
    @check_session
    def delete_post(cls, post, session=None, delete_files=False):
        comments = session.query(Comment.id).filter(Comment.post_id == post.id)
        cls.bulk_delete(Comment, session, comments)
        files = []
        if delete_files:
            # First query full content model so that file paths can be retrieved.
            content = session.query(Content).filter(Content.post_id == post.id)
            files = [c.get_full_file_path() for c in content]
        # Query content id's so that the query can be bulk deleted
        content_ids = session.query(Content.id).filter(Content.post_id == post.id)
        cls.bulk_delete(Content, session, content_ids)
        session.delete(post)
        for file in files:
            system_util.delete_file(file)
        session.commit()

    @classmethod
    @check_session
    def delete_content(cls, content, delete_post=False, session=None, delete_file=False):
        if delete_post:
            session.delete(content.post)
        if delete_file:
            system_util.delete_file(content.get_full_file_path())
        session.delete(content)
        session.commit()

    @classmethod
    def bulk_delete(cls, model, session, query):
        """
        This method is more convoluted than should be necessary, but sqlalchemy does not have adequate batch operation
        handling for this purpose.  So the subquery method used below is the only way to bulk delete a query with a
        limit, and a query with an offset and limit is the only way to delete a query which may contain more than 1,000
        items.  So here we are.
        :param model: The database model in the query which will be deleted.
        :param session: The session that has been used for the supplied query.
        :param query: The query containing the id's of the objects to be deleted.
        """
        batch_count = math.ceil(query.count() / 999)
        offset = 0
        for batch in range(batch_count):
            sub_query = query.offset(offset).limit(999).subquery()
            batch_query = session.query(model).filter(model.id.in_(sub_query))
            batch_query.delete(synchronize_session='fetch')
            offset += 1000
