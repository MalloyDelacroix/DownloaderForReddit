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


class MessageDialog(object):
    """
    A class that holds various message boxes that are accessed by the GUI.  When implementing one of these message
    dialogs from the GUI it is important to provide an instance of the GUI 'self' with the function call.
    """

    def __init__(self):
        pass

    def generic_message(self, title='', text=''):
        reply = message.information(self, title, text)
        return reply == message.Ok

    def no_user_list(self):
        text = 'There are no user lists available. To add a user, please add a user list'
        reply = message.warning(self, 'No User List', text, message.Ok)
        return reply == message.Ok

    def no_subreddit_list(self):
        text = 'There are no subreddit lists available. To add a subreddit please add a subreddit list'
        reply = message.warning(self, 'No Subreddit List', text, message.Ok)
        return reply == message.Ok

    def no_reddit_object_selected(self, type):
        text = 'No %s selected' % type
        reply = message.information(self, 'No Selection', text, message.Ok)
        return reply == message.Ok

    def failed_to_save(self):
        text = 'Sorry, the user and subreddit lists save attempt was not successful.  Please try again.'
        reply = message.information(self, 'Save Failed', text, message.Ok)
        return reply == message.Ok

    def cannot_save_while_running(self):
        text = 'Cannot save while downloader is running.  Please wait for the download session to finish and try again'
        reply = message.information(self, 'Cannot Save While Running', text, message.Ok)
        return reply == message.Ok

    def remove_reddit_object(self, name):
        text = 'Are you sure you sure you want to remove %s from the list along with all associated information?' % name
        reply = message.question(self, 'Remove %s' % name, text, message.Yes, message.No)
        return reply == message.Yes

    def remove_user_list(self):
        text = 'Are you sure you want to remove this list? Information for every user in the list will be lost'
        reply = message.warning(self, 'Remove User List?', text, message.Ok, message.Cancel)
        return reply == message.Ok

    def remove_subreddit_list(self):
        text = 'Are you sure you want to remove this list? Information for every subreddit in the list will be lost'
        reply = message.warning(self, 'Remove Subreddit List?', text, message.Ok, message.Cancel)
        return reply == message.Ok

    def reddit_object_not_valid(self, name, type_):
        type_ = type_.lower()
        text = '%s is not a valid %s. Would you like to remove this %s from the %s list?' % (name, type_, type_, type_)
        reply = message.question(self, 'Invalid Object', text, message.Yes, message.No)
        return reply == message.Yes

    def reddit_object_forbidden(self, name, type_):
        type_ = type_.lower()
        text = f'Forbidden: You do not have permission to access {name}.  Would you like to remove this {type_} from ' \
            f'the {type_} list?'
        reply = message.question(self, 'Forbidden Object', text, message.Yes, message.No)
        return reply == message.Yes
    
    def user_not_valid(self, user):
        text = '%s is not a valid user. Would you like to remove this user from the user list?' % user
        reply = message.information(self, 'Invalid User', text, message.Yes, message.No)
        return reply == message.Ok

    def subreddit_not_valid(self, sub):
        text = '%s is not a valid subreddit. Would you like to remove this sub from the subreddit list?' % sub
        reply = message.information(self, 'Invalid Subreddit', text, message.Yes, message.No)
        return reply == message.Ok

    def not_valid_name(self, name):
        text = 'Sorry, "%s" is not a valid name' % name
        reply = message.information(self, 'Invalid Name', text, message.Ok)
        return reply == message.Ok

    def invalid_names(self, name_list):
        text = '%s\nare not valid names' % '\n'.join(x for x in name_list)
        reply = message.information(self, 'Invalid Names', text, message.Ok)
        return reply == message.Ok

    def name_in_list(self, name):
        text = '"%s" is already in the list' % name
        reply = message.information(self, 'Existing Name', text, message.Ok)
        return reply == message.Ok

    def names_in_list(self, name_list):
        text = '%s\nalready in list' % '\n'.join(x for x in name_list)
        reply = message.information(self, 'Existing Names', text, message.Ok)
        return reply == message.Ok

    def no_download_folder(self, object_type):
        object_type = object_type.lower()
        text = 'The %s you selected does not appear to have a download folder. This is likely because nothing has ' \
               'been downloaded for this %s yet.' % (object_type, object_type)
        reply = message.information(self, 'Folder Does Not Exist', text, message.Ok)
        return reply == message.Ok

    def no_users_downloaded(self):
        text = 'No users have been downloaded yet'
        reply = message.information(self, 'No Content', text, message.Ok)
        return reply == message.Ok

    def nothing_to_download(self):
        text = 'Nothing to download. Please add users or subreddits you would like to download from.'
        reply = message.information(self, 'Nothing to Download', text, message.Ok)
        return reply == message.Ok

    def downloader_running_warning(self):
        text = 'The user finder is still currently running.  Closing now may cause unexpected behaviour and corrupted '\
               'files.  Are you sure you want to close?'
        reply = message.warning(self, 'User Finder Still Running', text, message.Ok, message.Cancel)
        return reply == message.Ok

    def restore_defaults_warning(self):
        text = 'Defaults have been restored. If you save now, any settings controlled from this window will be ' \
               'restored to their original values.\n\nAny user or subreddit who\'s custom settings have been changed ' \
               'will also be restored to their default values.\n\nDo you wish to proceed?'
        reply = message.warning(self, 'Defaults Restored', text, message.Ok, message.Cancel)
        return reply == message.Ok

    def no_imgur_client(self):
        text = 'No Imgur client is detected. You must have an Imgur client in order to download content from ' \
               'imgur.com. Please see settings menu and click on the "Imgur Client Information" in the top right for ' \
               'instuctions on how to obtain an imgur client and enter its credentials for use with this application'
        reply = message.information(self, 'No Imgur Client', text, message.Ok)
        return reply == message.Ok

    def invalid_imgur_client(self):
        text = 'The Imgur client you are useing is not valid. Please see the imgur client dialog for instructions on ' \
               'how to obtain a valid client id and secret.  This dialog can be accessed through the settings menu'
        reply = message.information(self, 'Invalid Imgur Client', text, message.Ok)
        return reply == message.Ok

    def user_manual_not_found(self):
        text = 'The user manual cannot be found.  This is most likely because the manual has been moved from the ' \
               'expected location, or renamed to something the application is not expecting.  To correct the issue ' \
               'please move the user manual back to the source folder and ensure it is named ' \
               '"The Downloader For Reddit - User Manual.pdf"'
        reply = message.information(self, 'User Manual Not Found', text, message.Ok)
        return reply == message.Ok

    def up_to_date_message(self):
        text = 'You are running the latest version of The Downloader for Reddit'
        reply = message.information(self, 'Up To Date', text, message.Ok)
        return reply == message.Ok

    def update_reddit_objects_message(self):
        text = "Saved reddit objects are from a previous version of the program and are no\n" \
               "longer compatible. These objects will now be updated to the latest version\n" \
               "and the application will be saved. All of the objects settings and download list\n" \
               "will be carried over to new objects.\n" \
               "If you do not update these objects, the saved objects will not work correctly\n" \
               "and will most likely cause the application to crash"
        reply = message.information(self, "Update Reddit Objects", text, message.Ok, message.Cancel)
        return reply == message.Ok

    def unsaved_close_message(self):
        text = "Save changes to Downloader For Reddit?"
        reply = message.question(self, "Save Changes?", text, message.Yes | message.No | message.Cancel, message.Cancel)
        if reply == message.Yes:
            return "SAVE"
        elif reply == message.No:
            return "CLOSE"
        else:
            return "CANCEL"

    def invalid_file_path(self):
        text = 'The selected file/folder is not valid or is of an incompatible format'
        reply = message.information(self, 'Invalid Selection', text, message.Ok)
        return reply == message.Ok

    def save_file_permission_denied(self, save_path):
        text = 'A save file could not be created at this location: %s\nThis likely means this application does not ' \
               'have permission to save files to this location and will be unable to save any user or subreddit ' \
               'settings.\nIf this problem persists, please open an issue on this applications github page.' % save_path
        reply = message.information(self, 'Save Permission Denied', text, message.Ok)
        return reply == message.Ok

    def failed_to_rename_error(self, object_name):
        text = '%s was removed from the download list, but the folder was not able to be renamed' % object_name
        reply = message.information(self, 'Rename Failure', text, message.Ok)
        return reply == message.Ok

    def overwrite_save_file_question(self):
        text = 'A save file is already present in the data directory.\nDo you want to overwrite the save file(s)?\n' \
               'This action cannot be undone'
        reply = message.question(self, 'Overwrite File?', text, message.Yes, message.No)
        return reply == message.Yes

    def ffmpeg_warning(self):
        text = 'Ffmpeg not detected.  Videos hosted by reddit will be downloaded as two separate files (video and ' \
               'audio) and cannot be merged without ffmpeg.  See help menu for more information.\n\nThis dialog will ' \
               'not display again after save.\n\nDo you want to disable reddit video download?'
        reply = message.information(self, 'ffmpeg Not Installed', text, message.Yes, message.No)
        return reply == message.Yes
