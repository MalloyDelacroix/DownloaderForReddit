from PyQt5.QtCore import QObject, pyqtSignal

from .message import MessageType


class MessageReceiver(QObject):

    text_output = pyqtSignal(object)
    non_text_output = pyqtSignal(object)

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

    def run(self):
        while self.continue_run:
            message = self.queue.get()
            if message is not None:
                try:
                    if message.message is None:
                        self.non_text_output.emit()
                    else:
                        self.text_output.emit(message)
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
