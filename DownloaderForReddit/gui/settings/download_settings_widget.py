from DownloaderForReddit.guiresources.settings.download_settings_widget_auto import Ui_DownloadSettingsWidget
from .abstract_settings_widget import AbstractSettingsWidget
from DownloaderForReddit.utils import injector
from DownloaderForReddit.database.models import RedditObjectList
from DownloaderForReddit.core.reddit_object_creator import RedditObjectCreator


class DownloadSettingsWidget(AbstractSettingsWidget, Ui_DownloadSettingsWidget):

    def __init__(self):
        super().__init__()
        self.db = injector.get_database_handler()
        self.session = self.db.get_session()

        self.list_map = {}

        self.master_user_list = None
        self.master_subreddit_list = None
        self.make_master_lists()

        self.add_list(self.master_user_list, True)
        self.add_list(self.master_subreddit_list, True)
        for ro_list in self.session.query(RedditObjectList).order_by(RedditObjectList.id):
            self.add_list(ro_list)

        self.list_widget.currentItemChanged.connect(
            lambda x: self.list_settings_widget.set_objects([self.list_map[x.text()]]))

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
        self.list_widget.setCurrentRow(0)

    def apply_settings(self):
        self.set_from_master()
        self.session.commit()

    def set_from_master(self):
        self.settings.user_download_defaults = self.master_user_list.get_default_dict()
        self.settings.subreddit_download_defaults = self.master_subreddit_list.get_default_dict()

    def close(self):
        self.session.close()
        super().close()
