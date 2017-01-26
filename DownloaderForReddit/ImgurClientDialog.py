"""
Downloader for Reddit takes a list of reddit users and subreddits and downloads content posted to reddit either by the
users or on the subreddits.


Copyright (C) 2017, Kyle Hickey


This file is part of the Downloader for Reddit.

Downloader for Reddit is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Downloader for Reddit is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Downloader for Reddit.  If not, see <http://www.gnu.org/licenses/>.
"""


from PyQt5 import QtWidgets, QtCore

from ImgurClientDialog_auto import Ui_imgur_client_dialog


class ImgurClientDialog(QtWidgets.QDialog, Ui_imgur_client_dialog):
    """
    A dialog where the users person imgur client information is entered.  Also contains instructions on how to get an
    imgur client
    """
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)

        self.settings = QtCore.QSettings('ApexSoftware', 'RedditDownloader')

        self.client_id_line_edit = self.lineEdit
        self.client_secret_line_edit = self.lineEdit_2
        self.imgur_client_help_button.clicked.connect(self.help_dialog)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.close)

        self.lineEdit.setText(self.settings.value('lineEdit', '', type=str))
        self.lineEdit_2.setText(self.settings.value('lineEdit_2', '', type=str))

    def help_dialog(self):
        help_message = QtWidgets.QMessageBox()
        help_message.setWindowTitle('Imgur Client Help')
        help_message.setText('You must supply your own imgur client id and client secret in order for this app to use '
                             'the imgur api.<br><br>Due to the limits imposed by the imgur api, it is necessary for '
                             'each user to get their own credentials from imgur.com and supply them to the app for '
                             'personal use.<br>Each client is only allowed 12,200 requests per day, so to keep '
                             'each user from running out of requests, this client information is not '
                             'supplied by the app.<br><br>Please follow the link below to obtain an imgur client-id'
                             'and client-secret. You will need an imgur account<br><br>Recommended details to enter:'
                             '<br>Application name: Downloader for Reddit<br>Authorization type: Anonymous usage '
                             'without authorization<br>Authorization callback url: https://google.com (any valid url '
                             'will work here and it does not matter for anonymous usage)<br>Application website: setup '
                             'for github<br>Email: Your email address to email your credentials to.')
        # TODO: Once a git-hub page is set up for this, change the website above to the git-gub page
        help_message.setTextFormat(QtCore.Qt.RichText)
        help_message.setInformativeText("<a href='https://api.imgur.com/oauth2/addclient'>https://api.imgur.com/oauth2/addclient<a/>")
        help_message.exec_()

    def accept(self):
        self.settings.setValue('lineEdit', self.lineEdit.text())
        self.settings.setValue('lineEdit_2', self.lineEdit_2.text())
        super().accept()
