from enum import Enum
from typing import Optional

from ..utils import injector


class MessageType(Enum):

    TEXT_OUTPUT = 1
    POTENTIAL_EXTRACTION = 2
    ACTUAL_EXTRACTION = 3
    POTENTIAL_DOWNLOAD = 4
    ACTUAL_DOWNLOAD = 5
    EXTRACTION_ERROR = 6
    DOWNLOAD_ERROR = 7


class Message:

    message_queue = injector.get_message_queue()

    def __init__(self, message_type: MessageType, message: Optional[str] = None):
        self.message_type = message_type
        self.message = message

    @classmethod
    def send(cls, message_type: MessageType, message: Optional[str] = None) -> None:
        m = cls(message_type, message)
        cls.message_queue.put(m)

    @classmethod
    def send_text(cls, message: str) -> None:
        cls.send(MessageType.TEXT_OUTPUT, message)

    @classmethod
    def send_extraction_error(cls, message: str):
        cls.send(MessageType.EXTRACTION_ERROR, message)

    @classmethod
    def send_download_error(cls, message: str):
        cls.send(MessageType.DOWNLOAD_ERROR, message)
