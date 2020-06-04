from PyQt5.QtCore import QObject, pyqtSignal

from .message import MessageType


class MessageReceiver(QObject):

    text_output = pyqtSignal(str)
    potential_extraction = pyqtSignal()
    actual_extraction = pyqtSignal()
    potential_download = pyqtSignal()
    actual_download = pyqtSignal()
    extraction_error = pyqtSignal(str)
    download_error = pyqtSignal(str)

    finished = pyqtSignal()

    def __init__(self, queue):
        """
        A class monitors the supplied instance of the queue that is common throughout all parts of the program which
        emits a signal to update the main GUI window when something comes through the queue.  This class will be moved
        operate from another thread

        :param queue: An instance of the queue supplied in the "main" function
        """
        super().__init__()
        self.queue = queue
        self.continue_run = True

        self.signal_dict = {
            MessageType.TEXT_OUTPUT: self.text_output,
            MessageType.POTENTIAL_EXTRACTION: self.potential_extraction,
            MessageType.ACTUAL_EXTRACTION: self.actual_extraction,
            MessageType.POTENTIAL_DOWNLOAD: self.potential_download,
            MessageType.ACTUAL_DOWNLOAD: self.actual_download,
            MessageType.EXTRACTION_ERROR: self.extraction_error,
            MessageType.DOWNLOAD_ERROR: self.download_error
        }

    def run(self):
        while self.continue_run:
            message = self.queue.get()
            if message is not None:
                try:
                    signal = self.signal_dict[message.message_type]
                    if message.message is None:
                        signal.emit()
                    else:
                        signal.emit(message.message)
                except AttributeError:
                    print(f'\nFailed output:\n{message}\n')
        self.finished.emit()

    def stop_run(self):
        """
        Stops the receiver from running which allows threads to end cleanly.  None is added to the queue because it will
        block until it receives something
        """
        self.continue_run = False
        self.queue.put(None)
