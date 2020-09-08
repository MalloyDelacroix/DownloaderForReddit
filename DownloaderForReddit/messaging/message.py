from enum import Enum
from typing import Optional

from ..utils import injector


class MessageType(Enum):

    TEXT = 1

    POTENTIAL_PROGRESS = 2
    ACTUAL_PROGRESS = 3
    POTENTIAL_COUNT = 4
    ACTUAL_COUNT = 5


class MessagePriority(Enum):

    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5


class Message:

    message_queue = injector.get_message_queue()

    def __init__(self, message_type: MessageType, message: Optional[str] = None,
                 priority: MessagePriority = MessagePriority.INFO):
        self.message_type = message_type
        self.message = message
        self.priority = priority

    @property
    def output(self):
        return f'{self.priority.name}:  {self.message}'

    @classmethod
    def send(cls, message_type: MessageType, message: Optional[str] = None,
             priority: MessagePriority = MessagePriority.INFO) -> None:
        m = cls(message_type, message, priority)
        cls.message_queue.put(m)

    @classmethod
    def send_debug(cls, message: str) -> None:
        cls.send(MessageType.TEXT, message, MessagePriority.DEBUG)

    @classmethod
    def send_info(cls, message: str) -> None:
        cls.send(MessageType.TEXT, message, MessagePriority.INFO)

    @classmethod
    def send_warning(cls, message: str) -> None:
        cls.send(MessageType.TEXT, message, MessagePriority.WARNING)

    @classmethod
    def send_error(cls, message: str) -> None:
        cls.send(MessageType.TEXT, message, MessagePriority.ERROR)

    @classmethod
    def send_critical(cls, message: str) -> None:
        cls.send(MessageType.TEXT, message, MessagePriority.CRITICAL)

    @classmethod
    def send_extraction_error(cls, message: str):
        cls.send(MessageType.POTENTIAL_PROGRESS, priority=MessagePriority.ERROR)
        cls.send(MessageType.TEXT, message, MessagePriority.ERROR)

    @classmethod
    def send_download_error(cls, message: str):
        cls.send(MessageType.POTENTIAL_PROGRESS, priority=MessagePriority.ERROR)
        cls.send(MessageType.TEXT, message, MessagePriority.ERROR)
