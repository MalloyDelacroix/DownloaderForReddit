from PyQt5.QtWidgets import QListWidgetItem


class CustomListItem(QListWidgetItem):

    def __init__(self):
        super().__init__()
        self.path = None
