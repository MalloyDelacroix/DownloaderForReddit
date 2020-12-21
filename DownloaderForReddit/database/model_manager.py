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
        posts = session.query(Post).filter(Post.significant_reddit_object_id == reddit_object.id)

        def delete_posts(post_query, session, delete_files):
            for post in post_query:
                content = session.query(Content).filter(Content.post_id == post.id)
                if delete_files:
                    for c in content:
                        system_util.delete_file(c.get_full_file_path())
                content.delete(synchronize_session='fetch')
                comments = session.query(Comment).filter(Comment.post_id == post.id)
                comments.delete(synchronize_session='fetch')
            # SqlAlchemy is being a real pain in the ass about deleting these posts easily.  So this is a ridiculous,
            # convoluted way to do it instead.
            post_ids = [x.id for x in post_query]
            session.query(Post).filter(Post.id.in_(post_ids)).delete(synchronize_session='fetch')

        cls.batch_operation(posts, delete_posts, session=session, delete_files=delete_files)

        session.query(ListAssociation).filter(ListAssociation.reddit_object_id == reddit_object.id).delete()
        session.delete(reddit_object)
        session.commit()

    @classmethod
    @check_session
    def delete_post(cls, post, session=None, delete_files=False):
        comments = session.query(Comment).filter(Comment.post_id == post.id)
        cls.batch_operation(comments, cls.delete_query)
        content = session.query(Content).filter(Content.post_id == post.id)
        files = []
        if delete_files:
            files = [c.get_full_file_path() for c in content]
        cls.batch_operation(content, cls.delete_query)
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
    @check_session
    def delete_comment(cls, comment, delete_post=False, delete_files=False, session=None):
        if delete_post:
            session.delete(comment.post)
        for content in comment.content:
            cls.delete_content(content, delete_file=delete_files, session=session)
        session.delete(comment)
        session.commit()

    @classmethod
    def delete_query(cls, query):
        query.delete(synchronize_session='fetch')

    @classmethod
    def batch_operation(cls, query, method, *args, **kwargs):
        batch_count = math.ceil(query.count() / 999)
        offset = 0
        for batch in range(batch_count):
            batch_query = query.offset(offset).limit(999)
            method(batch_query, *args, **kwargs)
            offset += 1000
