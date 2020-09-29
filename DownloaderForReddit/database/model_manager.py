from ..utils import injector
from .models import Post, Content, Comment, ListAssociation


def check_session(method):
    def check(*args, **kwargs):
        if kwargs.get('session', None) is None:
            with ModelManger.db.get_scoped_update_session() as session:
                kwargs['session'] = session
                return method(*args, **kwargs)
        return method(*args, **kwargs)

    return check


class ModelManger:

    db = injector.get_database_handler()

    @classmethod
    @check_session
    def delete_reddit_object(cls, reddit_object, session=None):
        """
        Deletes the supplied reddit object and all associated posts, content, and comment items.
        :param reddit_object: The reddit object to be deleted.
        :param session: The currently open session to use for the interaction.  Defaults to None.
        :return: True if the operation was successful, false if not.
        """
        posts = session.query(Post).filter(Post.significant_reddit_object_id == reddit_object.id)
        post_ids = [x.id for x in posts]
        session.query(Content).filter(Content.post_id.in_(post_ids)).delete(synchronize_session='fetch')
        session.query(Comment).filter(Comment.post_id.in_(post_ids)).delete(synchronize_session='fetch')
        posts.delete(synchronize_session='fetch')
        session.query(ListAssociation).filter(ListAssociation.reddit_object_id == reddit_object.id).delete()
        session.delete(reddit_object)

    @classmethod
    @check_session
    def delete_post(cls, post, session=None):
        session.query(Comment).filter(Comment.post_id == post.id).delete(synchronize_session='fetch')
        session.query(Content).fitler(Content.post_id == post.id).delete(synchronize_session='fetch')
        session.delete(post)

    @classmethod
    @check_session
    def delete_content(cls, content, delete_post=False, session=None):
        if delete_post:
            session.delete(content.post)
        session.delete(content)

    @classmethod
    @check_session
    def delete_comment(cls, comment, delete_post=False, session=None):
        if delete_post:
            session.delete(comment.post)
        session.delete(comment)
