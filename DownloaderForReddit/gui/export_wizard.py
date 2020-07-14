import os
from datetime import datetime
from PyQt5.QtWidgets import QWizard, QFileDialog

from ..guiresources.export_wizard_auto import Ui_ExportWizard
from ..utils import injector
from ..utils.exporters import json_exporter


class ExportWizard(QWizard, Ui_ExportWizard):

    def __init__(self, export_list, list_type, suggested_name=None):
        QWizard.__init__(self)
        self.setupUi(self)
        self.settings_manager = injector.get_settings_manager()
        self.export_list = export_list
        self.list_type = list_type
        if suggested_name is None:
            name = f"{datetime.now().strftime('%m-%d-%Y--%H-%M-%S')} Export"
        else:
            name = suggested_name
        self.export_path_line_edit.setText(os.path.join(self.settings_manager.export_file_path, name))
        self.path_dialog_button.clicked.connect(self.select_export_path)

        self.export_map = {
            'REDDIT_OBJECT_LIST': json_exporter.export_reddit_object_list_to_json,
            'REDDIT_OBJECT': json_exporter.export_reddit_objects_to_json,
            'POST': json_exporter.export_posts_to_json,
            'COMMENT': json_exporter.export_comments_to_json,
            'CONTENT': json_exporter.export_content_to_json,
        }

    @property
    def extension(self):
        if self.csv_export_radio.isChecked():
            return 'csv'
        else:
            return 'json'

    def select_export_path(self):
        file_path, _ = QFileDialog.getSaveFileName(self, 'Export Path', self.export_path_line_edit.text(),
                                                   self.extension)
        if file_path is not None and file_path != '':
            self.export_path_line_edit.setText(file_path)

    def accept(self):
        self.export()
        super().accept()

    def export(self):
        if self.json_export_radio.isChecked():
            self.export_json()
        else:
            self.export_csv()

    def export_json(self):
        export_method = self.export_map[self.list_type]
        export_method(self.export_list, f'{self.export_path_line_edit.text()}.json',
                      nested=self.export_complete_nested_radio.isChecked())

    def export_csv(self):
        pass
