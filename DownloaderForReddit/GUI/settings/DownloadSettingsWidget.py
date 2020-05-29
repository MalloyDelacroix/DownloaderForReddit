from DownloaderForReddit.GUI_Resources.settings.DownloadSettingsWidget_auto import Ui_DownloadSettingsWidget
from .AbstractSettingsWidget import AbstractSettingsWidget
from DownloaderForReddit.Utils import Injector
from DownloaderForReddit.Database.Models import RedditObjectList
from DownloaderForReddit.Core.RedditObjectCreator import RedditObjectCreator


class DownloadSettingsWidget(AbstractSettingsWidget, Ui_DownloadSettingsWidget):

    def __init__(self):
        super().__init__()
        self.db = Injector.get_database_handler()
        self.session = self.db.get_session()

        self.list_map = {}

        self.master_list = None

        for ro_list in self.session.query(RedditObjectList).order_by(RedditObjectList.id):
            self.add_list(ro_list)

        self.list_widget.currentItemChanged.connect(
            lambda x: self.list_settings_widget.set_objects([self.list_map[x.text()]]))

    def make_master_lists(self):
        creator = RedditObjectCreator('USER')
        return creator.create_reddit_object_list('Master List', False)

    def add_list(self, ro_list):
        item = f'{ro_list.name}  [{ro_list.list_type}]'
        self.list_map[item] = ro_list
        self.list_widget.addItem(item)

    def load_settings(self):
        self.list_widget.setCurrentRow(0)

    def apply_settings(self):
        self.session.commit()

    def set_from_master(self):
        pass

    def close(self):
        self.session.close()
        super().close()
