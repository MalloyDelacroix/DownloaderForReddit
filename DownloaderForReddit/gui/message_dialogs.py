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


from PyQt5.QtWidgets import QMessageBox as Message
from PyQt5.QtWidgets import QCheckBox


def generic_message(parent, title='', text=''):
    reply = Message.information(parent, title, text)
    return reply == Message.Ok


def no_user_list(parent):
    text = 'There are no user lists available. To add a user, please add a user list'
    reply = Message.warning(parent, 'No User List', text, Message.Ok)
    return reply == Message.Ok


def no_subreddit_list(parent):
    text = 'There are no subreddit lists available. To add a subreddit please add a subreddit list'
    reply = Message.warning(parent, 'No Subreddit List', text, Message.Ok)
    return reply == Message.Ok


def no_reddit_object_selected(parent, type):
    text = 'No %s selected' % type
    reply = Message.information(parent, 'No Selection', text, Message.Ok)
    return reply == Message.Ok


def remove_reddit_object(parent, name):
    text = f'Are you sure you want to remove {name} from this list?  {name} will remain in the database ' \
           f'all associated information'
    return optional_question_dialog(parent, f'Remove {name}?', text)


def remove_reddit_objects(parent, reddit_objects):
    ro_type = reddit_objects[0].object_type
    if len(reddit_objects) > 1:
        text = f'Are you sure you want to remove {len(reddit_objects)} from the list?  These {ro_type.lower()}s will ' \
               f'remain in the database along with all associated information.'
    else:
        text = f'Are you sure you want to remove {reddit_objects[0].name} from the list?  {reddit_objects[0].name} ' \
               f'will remain in the database along with all associated information.'
    return optional_question_dialog(parent, f'Remove {reddit_objects[0].name}?' if len(reddit_objects) > 1 else
                                    f'Remove {len(reddit_objects)} {ro_type.lower()}s?', text)


def remove_list(parent, list_type):
    text = f'Are you sure you want to remove this list?  Only the list information will be deleted.  ' \
           f'{list_type.title()}s in the list will remain in the database.'
    return optional_question_dialog(parent, f'Remove {list_type.title()} List?', text)


def reddit_object_not_valid(parent, name, type_):
    type_ = type_.lower()
    text = '%s is not a valid %s. Would you like to remove this %s from the %s list?' % (name, type_, type_, type_)
    reply = Message.question(parent, 'Invalid Object', text, Message.Yes, Message.No)
    return reply == Message.Yes


def reddit_object_forbidden(parent, name, type_):
    type_ = type_.lower()
    text = f'Forbidden: You do not have permission to access {name}.  Would you like to remove this {type_} from ' \
        f'the {type_} list?'
    reply = Message.question(parent, 'Forbidden Object', text, Message.Yes, Message.No)
    return reply == Message.Yes


def user_not_valid(parent, user):
    text = '%s is not a valid user. Would you like to remove this user from the user list?' % user
    reply = Message.information(parent, 'Invalid User', text, Message.Yes, Message.No)
    return reply == Message.Ok


def subreddit_not_valid(parent, sub):
    text = '%s is not a valid subreddit. Would you like to remove this sub from the subreddit list?' % sub
    reply = Message.information(parent, 'Invalid Subreddit', text, Message.Yes, Message.No)
    return reply == Message.Ok


def not_valid_name(parent, name):
    text = 'Sorry, "%s" is not a valid name' % name
    reply = Message.information(parent, 'Invalid Name', text, Message.Ok)
    return reply == Message.Ok


def invalid_names(parent, name_list):
    text = '%s\nare not valid names' % '\n'.join(x for x in name_list)
    reply = Message.information(parent, 'Invalid Names', text, Message.Ok)
    return reply == Message.Ok


def no_download_folder(parent, object_type):
    object_type = object_type.lower()
    text = 'The %s you selected does not appear to have a download folder. This is likely because nothing has ' \
           'been downloaded for this %s yet.' % (object_type, object_type)
    reply = Message.information(parent, 'Folder Does Not Exist', text, Message.Ok)
    return reply == Message.Ok


def user_manual_not_found(parent):
    text = 'The user manual cannot be found.  This is most likely because the manual has been moved from the ' \
           'expected location, or renamed to something the application is not expecting.  To correct the issue ' \
           'please move the user manual back to the source folder and ensure it is named ' \
           '"The Downloader For Reddit - User Manual.pdf"'
    reply = Message.information(parent, 'User Manual Not Found', text, Message.Ok)
    return reply == Message.Ok


def up_to_date_message(parent):
    text = 'You are running the latest version of The Downloader for Reddit'
    reply = Message.information(parent, 'Up To Date', text, Message.Ok)
    return reply == Message.Ok


def invalid_file_path(parent):
    text = 'The selected file/folder is not valid or is of an incompatible format'
    reply = Message.information(parent, 'Invalid Selection', text, Message.Ok)
    return reply == Message.Ok


def failed_to_rename_error(parent, object_name):
    text = '%s was removed from the download list, but the folder was not able to be renamed' % object_name
    reply = Message.information(parent, 'Rename Failure', text, Message.Ok)
    return reply == Message.Ok


def ffmpeg_warning(parent):
    text = 'Ffmpeg not detected.  Videos hosted by reddit will be downloaded as two separate files (video and ' \
           'audio) and cannot be merged without ffmpeg.  See help menu for more information.\n\nThis dialog will ' \
           'not display again after save.\n\nDo you want to disable reddit video download?'
    reply = Message.information(parent, 'ffmpeg Not Installed', text, Message.Yes, Message.No)
    return reply == Message.Yes


def optional_info_dialog(parent, title, text):
    dialog = Message(parent)
    dialog.setWindowTitle(title)
    dialog.setText(text)
    checkbox = QCheckBox('Do not show again')
    dialog.setCheckBox(checkbox)
    reply = dialog.exec_()
    return checkbox.isChecked()


def warning_question_dialog(parent, title, text):
    dialog = Message(parent)
    dialog.setIcon(Message.Warning)
    dialog.setWindowTitle(title)
    dialog.setText(text + '\n')
    dialog.setStandardButtons(Message.Yes | Message.No)
    dialog.setDefaultButton(Message.No)
    reply = dialog.exec_() == Message.Yes
    return reply


def optional_question_dialog(parent, title, text, checkbox_text='Do not show again'):
    dialog = Message(parent)
    dialog.setIcon(Message.Question)
    dialog.setWindowTitle(title)
    dialog.setText(text + '\n')
    checkbox = QCheckBox(checkbox_text)
    dialog.setCheckBox(checkbox)
    dialog.setStandardButtons(Message.Yes | Message.No)
    dialog.setDefaultButton(Message.No)
    dialog.setEscapeButton(Message.No)
    reply = dialog.exec_() == Message.Yes
    return reply, checkbox.isChecked()


def error_dialog(parent, title, text):
    dialog = Message(parent)
    dialog.setWindowTitle(title)
    dialog.setText(text)
    reply = dialog.exec_()
    return reply
