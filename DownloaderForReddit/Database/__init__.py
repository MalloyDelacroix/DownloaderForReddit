from sqlalchemy import event

from .Models import Post, Content
from ..Messaging.Message import Message, MessageType

from .DatabaseHandler import DatabaseHandler
from .Filters import (RedditObjectListFilter, RedditObjectFilter, DownloadSessionFilter, PostFilter, ContentFilter,
                      CommentFilter)
from .Models import (ListAssociation, RedditObjectList, RedditObject, User, Subreddit, DownloadSession, Post, Content,
                     Comment)


@event.listens_for(Post, 'after_insert')
def post_created(mapper, connection, target):
    Message.send(MessageType.POTENTIAL_EXTRACTION)


@event.listens_for(Post.extracted, 'set')
def post_extracted(target, value, oldValue, initiator):
    if value:
        Message.send(MessageType.ACTUAL_EXTRACTION)


@event.listens_for(Content, 'after_insert')
def content_created(mapper, connection, target):
    Message.send(MessageType.POTENTIAL_DOWNLOAD)


@event.listens_for(Content.downloaded, 'set')
def content_downloaded(target, value, oldvalue, initiator):
    if value:
        Message.send(MessageType.ACTUAL_DOWNLOAD)
