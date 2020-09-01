from PyQt5.QtWidgets import QLabel, QLineEdit, QFormLayout

from .abstract_settings_widget import AbstractSettingsWidget


class ImgurSettingsWidget(AbstractSettingsWidget):

    def __init__(self):
        super().__init__(init_ui=False)
        self.setWindowTitle('Imgur Settings')

        self.client_id_line_edit = QLineEdit()
        self.client_secret_line_edit = QLineEdit()
        self.mashape_key_line_edit = QLineEdit()

        layout = QFormLayout()
        self.setLayout(layout)

        layout.addRow(QLabel('Imgur client id:'), self.client_id_line_edit)
        layout.addRow(QLabel('Imgur client secret:'), self.client_secret_line_edit)
        layout.addRow(QLabel('Imgur mashape key:'), self.mashape_key_line_edit)

    @property
    def description(self):
        return 'Enter the credentials provided to you from imgur when you registered for the client.  If you do not ' \
               'yet have these credentials, instructions on how to register ' \
               '<a href="https://github.com/MalloyDelacroix/DownloaderForReddit#requirements">can be found here.</a>' \
               '<br><br>' \
               'If the standard allotted credits are unsuitable for your needs, you can purchase commercial api ' \
               'credentials <a href="https://rapidapi.com/imgur/api/imgur-9/pricing">from rapidapi.com</a> ' \
               '(free plans are also available) and enter the key in the "mashape key" box.'

    def load_settings(self):
        self.client_id_line_edit.setText(self.settings.imgur_client_id)
        self.client_secret_line_edit.setText(self.settings.imgur_client_secret)
        self.mashape_key_line_edit.setText(self.settings.imgur_mashape_key)

    def apply_settings(self):
        self.settings.imgur_client_id = self.client_id_line_edit.text()
        self.settings.imgur_client_secret = self.client_secret_line_edit.text()
        self.settings.imgur_mashape_key = self.mashape_key_line_edit.text()
