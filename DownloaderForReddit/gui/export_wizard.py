import os
from datetime import datetime
from PyQt5.QtWidgets import QWizard, QFileDialog

from ..guiresources.export_wizard_auto import Ui_ExportWizard
from ..utils import injector, system_util, general_utils
from ..utils.exporters import json_exporter, csv_exporter


class ExportWizard(QWizard, Ui_ExportWizard):

    def __init__(self, export_list, export_model, suggested_name=None, parent=None):
        QWizard.__init__(self, parent=parent)
        self.setupUi(self)
        self.settings_manager = injector.get_settings_manager()
        self.export_list = export_list
        self.export_model = export_model
        if suggested_name is None:
            formatted_date = general_utils.format_datetime(datetime.now())
            name = f"{general_utils.format_date_path(formatted_date)} Export"
        else:
            name = suggested_name
        self.export_path_line_edit.setText(system_util.join_path(self.settings_manager.export_file_path, name))
        self.path_dialog_button.clicked.connect(self.select_export_path)

        self.json_export_map = {
            'RedditObjectList': json_exporter.export_reddit_object_list_to_json,
            'RedditObject': json_exporter.export_reddit_objects_to_json,
            'Post': json_exporter.export_posts_to_json,
            'Comment': json_exporter.export_comments_to_json,
            'Content': json_exporter.export_content_to_json,
        }

        self.csv_export_radio.toggled.connect(self.toggle_nested_page)

    @property
    def extension(self):
        if self.csv_export_radio.isChecked():
            return 'csv'
        else:
            return 'json'

    def toggle_nested_page(self):
        """
        Toggles the nested page settings page on or off depending on the type of export to be performed.  CSV export
        files cannot be nested.
        """
        if self.csv_export_radio.isChecked():
            self.removePage(self.nextId())
        else:
            self.addPage(self.page_two)
            self.removePage(self.nextId())
            self.addPage(self.page_three)

    def select_export_path(self):
        file_path, _ = QFileDialog.getSaveFileName(self, 'Export Path', self.export_path_line_edit.text(),
                                                   self.extension)
        if file_path is not None and file_path != '':
            self.export_path_line_edit.setText(file_path)

    def accept(self):
        if self.export():
            super().accept()

    def export(self):
        if os.path.isdir(os.path.dirname(self.export_path_line_edit.text())):
            if self.json_export_radio.isChecked():
                self.export_json()
            else:
                self.export_csv()
            return True
        else:
            self.export_path_line_edit.setStyleSheet('border: 1px solid red;')
            return False

    def export_json(self):
        export_method = self.json_export_map[self.export_model.__name__]
        export_method(self.export_list, f'{self.export_path_line_edit.text()}.json',
                      nested=self.export_complete_nested_radio.isChecked())

    def export_csv(self):
        csv_exporter.export_csv(self.export_list, self.export_model, f'{self.export_path_line_edit.text()}.csv')
