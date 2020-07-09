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
        self.kwargs = kwargs

        self.list_map = {}

        self.master_user_list = None
        self.master_subreddit_list = None
        self.make_master_lists()

        self.add_list(self.master_user_list, True)
        self.add_list(self.master_subreddit_list, True)
        for ro_list in self.session.query(RedditObjectList).order_by(RedditObjectList.name):
            self.add_list(ro_list)

        self.list_widget.currentItemChanged.connect(
            lambda x: self.list_settings_widget.set_objects([self.list_map[x.text()]]))
        self.cascade_changes_checkbox.setChecked(self.settings.cascade_list_changes)

    @property
    def description(self):
        return 'Sets default download settings for the selected list.  Settings changed for each list will propagate ' \
               'to each reddit object held by the list unless that reddit object has its settings locked.  Reddit ' \
               'objects that are in multiple lists will be set by which ever list was modified last.  \n' \
               'If the selected list is a MASTER list, no settings will be propagated.  This list sets the global ' \
               'download defaults for the application and holds the default used when a new list is created.'

    def make_master_lists(self):
        creator = RedditObjectCreator('USER')
        self.master_user_list = creator.create_reddit_object_list('Master User List', commit=False)
        creator.list_type = 'SUBREDDIT'
        self.master_subreddit_list = creator.create_reddit_object_list('Master Subreddit List', commit=False)

    def add_list(self, ro_list, master=False):
        list_type = ro_list.list_type if not master else f'MASTER_{ro_list.list_type}'
        item = f'{ro_list.name}  [{list_type}]'
        self.list_map[item] = ro_list
        self.list_widget.addItem(item)

    def load_settings(self):
        open_list_id = self.kwargs.get('open_list_id', None)
        if open_list_id is None:
            self.list_widget.setCurrentRow(0)
        else:
            index = 0
            for ro_list in self.list_map.values():
                if ro_list.id == open_list_id:
                    self.list_widget.setCurrentRow(index)
                    break
                else:
                    index += 1

    def apply_settings(self):
        if self.cascade_changes_checkbox.isChecked():
            self.cascade_list_changes()
        self.settings.cascade_list_changes = self.cascade_changes_checkbox.isChecked()
        self.set_from_master()
        self.session.commit()

    def cascade_list_changes(self):
        for ro_list in self.list_map.values():
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
