from ..utils import injector, system_util
from .models import Post, Content, Comment, ListAssociation


def check_session(method):
    def check(*args, **kwargs):
        if kwargs.get('session', None) is None:
            with ModelManger.db.get_scoped_session() as session:
                kwargs['session'] = session
                return method(*args, **kwargs)
        return method(*args, **kwargs)

    return check


class ModelManger:

    db = injector.get_database_handler()

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
        """
        Deletes the supplied reddit object and all associated posts, content, and comment items.
        :param reddit_object: The reddit object to be deleted.
        :param session: The currently open session to use for the interaction.  Defaults to None.
        :return: True if the operation was successful, false if not.
        """
        posts = session.query(Post).filter(Post.significant_reddit_object_id == reddit_object.id)
        post_ids = [x.id for x in posts]
        content = session.query(Content).filter(Content.post_id.in_(post_ids))
        files = []
        if delete_files:
            files = [c.get_full_file_path() for c in content]
        content.delete(synchronize_session='fetch')
        session.query(Comment).filter(Comment.post_id.in_(post_ids)).delete(synchronize_session='fetch')
        posts.delete(synchronize_session='fetch')
        session.query(ListAssociation).filter(ListAssociation.reddit_object_id == reddit_object.id).delete()
        session.delete(reddit_object)
        for file in files:
            system_util.delete_file(file)
        session.commit()

    @classmethod
    @check_session
    def delete_post(cls, post, session=None, delete_files=False):
        session.query(Comment).filter(Comment.post_id == post.id).delete(synchronize_session='fetch')
        content = session.query(Content).filter(Content.post_id == post.id)
        files = []
        if delete_files:
            files = [c.get_full_file_path() for c in content]
        content.delete(synchronize_session='fetch')
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
