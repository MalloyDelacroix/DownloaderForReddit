from DownloaderForReddit.guiresources.settings.download_settings_widget_auto import Ui_DownloadSettingsWidget
from .abstract_settings_widget import AbstractSettingsWidget
from DownloaderForReddit.utils import injector
from DownloaderForReddit.database.models import RedditObjectList
from DownloaderForReddit.core.reddit_object_creator import RedditObjectCreator


class DownloadSettingsWidget(AbstractSettingsWidget, Ui_DownloadSettingsWidget):

    def __init__(self, **kwargs):
        super().__init__()
        self.db = injector.get_database_handler()
        self.session = self.db.get_session()
        self.main_window = kwargs.pop('main_window', None)
        self.kwargs = kwargs

        self.lists = []

        self.master_user_list = None
        self.master_subreddit_list = None
        self.make_master_lists()

        self.add_list(self.master_user_list, True)
        self.add_list(self.master_subreddit_list, True)
        for ro_list in self.session.query(RedditObjectList).order_by(RedditObjectList.name):
            self.add_list(ro_list)

        self.list_combo_box.currentIndexChanged.connect(
            lambda idx: self.list_settings_widget.set_objects([self.lists[idx]])
        )
        self.cascade_changes_checkbox.setChecked(self.settings.cascade_list_changes)

    @property
    def description(self):
        return 'Sets default download settings for the selected list. New settings will propagate ' \
               'to each user/subreddit currently in the list unless its settings are locked.' \
               'Users/subreddits in multiple lists will be set by which ever list was modified last.  \n\n' \
               'Master lists are special lists from which settings are copied when you create a new list. '\
               'These special lists contain no users/subreddits.'

    def make_master_lists(self):
        creator = RedditObjectCreator('USER')
        self.master_user_list = creator.create_reddit_object_list('Master User List', commit=False)
        creator.list_type = 'SUBREDDIT'
        self.master_subreddit_list = creator.create_reddit_object_list('Master Subreddit List', commit=False)

    def add_list(self, ro_list: RedditObjectList, is_master=False):
        list_type = ro_list.list_type if not is_master else f'MASTER_{ro_list.list_type}'
        name = f'{ro_list.name}  [{list_type}]'
        self.lists.append(ro_list)
        self.list_combo_box.addItem(name)

    def load_settings(self):
        open_list_id = self.kwargs.get('open_list_id', None)
        if open_list_id is None:
            self.list_combo_box.setCurrentIndex(0)
        else:
            for index, ro_list in enumerate(self.lists):
                if ro_list.id == open_list_id:
                    self.list_combo_box.setCurrentIndex(index)
                    break

    def apply_settings(self):
        if self.cascade_changes_checkbox.isChecked():
            self.cascade_list_changes()
        self.settings.cascade_list_changes = self.cascade_changes_checkbox.isChecked()
        self.set_from_master()
        self.session.commit()
        self.main_window.refresh_list_models()

    def cascade_list_changes(self):
        for ro_list in self.lists:
            if ro_list != self.master_user_list and ro_list != self.master_subreddit_list and ro_list.updated:
                for ro in ro_list.reddit_objects:
                    if not ro.lock_settings:
                        for key, value in ro_list.get_default_dict().items():
                            setattr(ro, key, value)

    def set_from_master(self):
        self.settings.user_download_defaults = self.master_user_list.get_default_dict()
        self.settings.subreddit_download_defaults = self.master_subreddit_list.get_default_dict()

    def close(self):
        self.session.close()
        super().close()
