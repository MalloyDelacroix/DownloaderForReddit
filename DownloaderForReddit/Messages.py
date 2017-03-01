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


from PyQt5.QtWidgets import QMessageBox as message
from PyQt5.QtWidgets import QDialog, QDialogButtonBox
from PyQt5.QtCore import pyqtSignal

from UnfinishedDownloadsWarningMessage_auto import Ui_Dialog
from UpdateDialog_auto import Ui_update_dialog_box

no_user_list_message = 'There are no user lists available. To add a user, please add a user list'
no_subreddit_list_message = 'There are no subreddit lists available. To add a subreddit please add a subreddit list'
no_user_selected_message = 'No user selected'
no_subreddit_selected_message = 'No subreddit selected'
failed_to_save_message = 'Sorry, the user and subreddit lists save attempt was not successful.  Please try again.'
remove_user_message = 'Are you sure you want to remove this user and all of their information?'
remove_subreddit_message = 'Are you sure you want to remove this subreddit and all of its information?'
remove_user_list_message = 'Are you sure you want to remove this list? Information for every user in the list will' \
                           ' be lost'
remove_subreddit_list_message = 'Are you sure you want to remove this list? Information for every subreddit in the ' \
                                'list will be lost'


class Message(object):
    """
    A class that holds various message boxes that are accessed by the GUI.  When implementing one of these message
    dialogs from the GUI it is important to provide an instance of the GUI 'self' with the function call.
    """

    def __init__(self):
        pass

    def no_user_list(self):
        reply = message.warning(self, 'Warning', no_user_list_message, message.Ok)
        if reply == message.Ok:
            pass

    def no_subreddit_list(self):
        reply = message.warning(self, 'No Subreddit List', no_subreddit_list_message, message.Ok)
        if reply == message.Ok:
            pass

    def no_user_selected(self):
        reply = message.information(self, 'No User Selected', no_user_selected_message, message.Ok)
        if reply == message.Ok:
            pass

    def no_subreddit_selected(self):
        reply = message.information(self, 'No Subreddit Selected', no_subreddit_selected_message, message.Ok)
        if reply == message.Ok:
            pass

    def failed_to_save(self):
        reply = message.information(self, 'Save Failed', failed_to_save_message, message.Ok)
        if reply == message.Ok:
            pass

    def remove_user(self):
        reply = message.information(self, 'Remove User?', remove_user_message, message.Ok, message.Cancel)
        if reply == message.Ok:
            return True
        else:
            return False

    def remove_subreddit(self):
        reply = message.information(self, 'Remove Subreddit?', remove_subreddit_message, message.Ok, message.Cancel)
        if reply == message.Ok:
            return True
        else:
            return False

    def remove_user_list(self):
        reply = message.warning(self, 'Remove User List?', remove_user_list_message, message.Ok, message.Cancel)
        if reply == message.Ok:
            return True
        else:
            return False

    def remove_subreddit_list(self):
        reply = message.warning(self, 'Remove Subreddit List?', remove_subreddit_list_message, message.Ok, message.Cancel)
        if reply == message.Ok:
            return True
        else:
            return False
    
    def user_not_valid(self, user):
        text = '%s is not a valid user. Would you like to remove this user from the user list?' % user
        reply = message.information(self, 'Invalid User', text, message.Yes, message.No)
        if reply == message.Yes:
            return True
        else:
            return False

    def subreddit_not_valid(self, sub):
        text = '%s is not a valid subreddit. Would you like to remove this sub from the subreddit list?' % sub
        reply = message.information(self, 'Invalid Subreddit', text, message.Yes, message.No)
        if reply == message.Yes:
            return True
        else:
            return False

    def not_valid_name(self):
        text = 'Sorry, that is not a valid name'
        reply = message.information(self, 'Invalid Name', text, message.Ok)
        if reply == message.Ok:
            return True
        else:
            return False

    def name_in_list(self):
        text = 'That name is already in the list'
        reply = message.information(self, 'Existing Name', text, message.Ok)
        if reply == message.Ok:
            return True
        else:
            return False

    def no_user_download_folder(self):
        text = 'The user you selected does not appear to have a download folder. This is likely because nothing has ' \
               'been downloaded for this user yet.'
        reply = message.information(self, 'Folder Does Not Exist', text, message.Ok)
        if reply == message.Ok:
            return True
        else:
            return False

    def no_subreddit_download_folder(self):
        text = 'The subreddit you selected does not appear to have a download folder. This is likely because nothing ' \
               'has been downloaded for this subreddit yet.'
        reply = message.information(self, 'Folder Does Not Exist', text, message.Ok)
        if reply == message.Ok:
            return True
        else:
            return False

    def no_users_downloaded(self):
        text = 'No users have been downloaded yet'
        reply = message.information(self, 'No Content', text, message.Ok)
        if reply == message.Ok:
            return True
        else:
            return False

    def nothing_to_download(self):
        text = 'Nothing to download. Please add users or subreddits you would like to download from.'
        reply = message.information(self, 'Nothing to Download', text, message.Ok)
        if reply == message.Ok:
            return True
        else:
            return False

    def downloader_running_warning(self):
        text = 'The user finder is still currently running.  Closing now may cause unexpected behaviour and corrupted ' \
               'files.  Are you sure you want to close?'
        reply = message.warning(self, 'User Finder Still Running', text, message.Ok, message.Cancel)
        if reply == message.Ok:
            return True
        else:
            return False

    def restore_defaults_warning(self):
        text = 'Defaults have been restored. If you save now, any settings controlled from this window will be ' \
               'restored to their original values.\n\nAny user or subreddit who\'s custom settings have been changed ' \
               'will also be restored to their default values.\n\nDo you wish to proceed?'
        reply = message.warning(self, 'Defaults Restored', text, message.Ok, message.Cancel)
        if reply == message.Ok:
            return True
        else:
            return False

    def no_imgur_client(self):
        text = 'No Imgur client is detected. You must have an Imgur client in order to download content from ' \
               'imgur.com. Please see settings menu and click on the "Imgur Client Information" in the top right for ' \
               'instuctions on how to obtain an imgur client and enter its credentials for use with this application'
        reply = message.information(self, 'No Imgur Client', text, message.Ok)
        if reply == message.Ok:
            return True
        else:
            return False

    def invalid_imgur_client(self):
        text = 'The Imgur client you are useing is not valid. Please see the imgur client dialog for instructions on ' \
               'how to obtain a valid client id and secret.  This dialog can be accessed through the settings menu'
        reply = message.information(self, 'Invalid Imgur Client', text, message.Ok)
        if reply == message.Ok:
            return True
        else:
            return False

    def user_manual_not_found(self):
        text = 'The user manual cannot be found.  This is most likely because the manual has been moved from the ' \
               'expected location, or renamed to something the application is not expecting.  To correct the issue ' \
               'please move the user manual back to the source folder and ensure it is named ' \
               '"The Downloader For Reddit - User Manual.pdf"'
        reply = message.information(self, 'User Manual Not Found', text, message.Ok)

    def up_to_date_message(self):
        text = 'You are running the latest version of The Downloader for Reddit'
        reply = message.information(self, 'Up To Date', text, message.Ok)
        if reply == message.Ok:
            return True
        else:
            return False

    def updater_cleanup_failure(self):
        text = 'This new version of The Downloader for Reddit came with a new updater.  There has been a problem in ' \
               'making the change to the new updater package.  What this means is that the program should still ' \
               'alert you that a new version is available, but it will most likely be unable to download and install ' \
               'it automatically.  In this event simply go to ' \
               'https://github.com/MalloyDelacroix/DownloaderForReddit/releases and manually download the release.  ' \
               'Make sure to copy your save_file from the current program location to the new location'
        reply = message.information(self, 'Updater Cleanup Failure', text, message.Ok)
        if reply == message.Ok:
            return True
        else:
            return False


class UnfinishedDownloadsWarning(QDialog, Ui_Dialog):

    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)

        self.button_box.button(QDialogButtonBox.Ok).setText('Close Anyway')
        self.button_box.button(QDialogButtonBox.Cancel).setText('Do Not Close')

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.close)

    def accept(self):
        super().accept()


class UpdateDialog(QDialog, Ui_update_dialog_box):

    def __init__(self, update_variables):
        super().__init__()
        self.setupUi(self)
        self.new_version = update_variables[0]
        self.update_size_mb = update_variables[1] / 1000000
        self.set_last_update = None
        self.label.setOpenExternalLinks(True)
        self.label.setWordWrap(True)
        self.label.setText('There is a new version of The Downloader for Reddit available for download.  Would you like'
                           ' to download this version?\n\nNew version: %s\nSize: %s\n\nIf you click "update" the '
                           'program will be closed and updated to the latest version.  Please finish any downloads '
                           'before clicking update' % (self.new_version, '{0:.1f}MB'.format(self.update_size_mb)))

        self.buttonBox.button(QDialogButtonBox.Ok).setText('Update')
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.check_and_close)

    def accept(self):
        super().accept()

    def check_and_close(self):
        if self.do_not_notify_checkbox.isChecked():
            self.set_last_update = self.new_version
        else:
            self.set_last_update = None
