from .quick_filter_settings_widget import QuickFilterSettingsWidget


class DefaultFilterSettingsWidget(QuickFilterSettingsWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Default Filter Settings')
        self.add_new_quick_filter_button.setVisible(False)

    @property
    def description(self):
        return 'Set default filters that will be loaded every time the selected type of database view dialog is ' \
               'opened.  Multiple filters can be combined together.'

    def load_settings(self):
        self.filters = self.settings.database_view_default_filters
        self.name_list_widget.addItems(self.filters.keys())
        self.name_list_widget.setCurrentRow(0)

    def apply_settings(self):
        self.settings.database_view_default_filters = self.filters
