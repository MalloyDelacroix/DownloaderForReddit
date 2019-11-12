from PyQt5.QtWidgets import QDialog, QPushButton, QLabel, QVBoxLayout, QHBoxLayout


class ExistingRedditObjectAddDialog(QDialog):

    """
    A dialog that gets user input as to whether or not to run a download when an attempt to add a reddit object to a
    list in which it already exists is made.
    """

    def __init__(self, object_name, object_type):
        QDialog.__init__(self)
        self.object_name = object_name
        self.object_type = object_type

        self.label = QLabel(
            f'{self.object_name} is already in the list.\n'
            f'Would you like to run a download for this {self.object_type.lower()}'
        )

        self.download_button = QPushButton(f'Download {self.object_type.lower()}')
        self.close_button = QPushButton('Close')
        self.download_button.clicked.connect(self.accept)
        self.close_button.clicked.connect(self.close)

        button_box = QHBoxLayout()
        button_box.setSpacing(15)
        button_box.addWidget(self.download_button)
        button_box.addWidget(self.close_button)
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.addWidget(self.label)
        layout.addItem(button_box)
        self.setLayout(layout)
