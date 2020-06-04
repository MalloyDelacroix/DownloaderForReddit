from PyQt5.QtWidgets import QDialog, QVBoxLayout
from PyQt5.QtCore import pyqtSignal


class BlankDialog(QDialog):

    closing = pyqtSignal()

    def __init__(self, parent=None):
        QDialog.__init__(self, parent=parent)
        self.setLayout(QVBoxLayout())

    def add_widgets(self, *widgets):
        for x in widgets:
            self.layout().addWidget(x)

    def closeEvent(self, event):
        self.closing.emit()
        super().closeEvent(event)
