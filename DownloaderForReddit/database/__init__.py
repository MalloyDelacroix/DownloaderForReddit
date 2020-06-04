from sqlalchemy import event

from ..scheduling.tasks import DownloadTask
from .models import Post, Content
from ..messaging.message import Message, MessageType


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
