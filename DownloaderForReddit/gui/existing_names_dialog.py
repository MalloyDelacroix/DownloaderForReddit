from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QCheckBox

from ..guiresources.existing_names_dialog_auto import Ui_ExistingNameDialog


class ExistingNamesDialog(QDialog, Ui_ExistingNameDialog):

    """
    Displays a list of existing reddit object names along with the lists that they are currently located in.  The user
    is asked for a response regarding whether or not they would like to add the reddit objects to the current list even
    though they are currently already in the database in other lists.
    """

    def __init__(self, existing_names):
        super().__init__()
        self.setupUi(self)
        self.existing_names = existing_names
        self.name_table_widget.setRowCount(len(self.existing_names))
        self.checkboxes = []
        self.decisions = {x: False for x in existing_names.keys()}

        self.select_all_checkbox.toggled.connect(self.toggle_all)
        self.setup_table()

    def setup_table(self):
        for row, (name, lists) in enumerate(self.existing_names.items()):
            checkbox = QCheckBox()
            checkbox.toggled.connect(lambda checked, name=name: self.decisions.update({name: checked}))
            self.checkboxes.append(checkbox)
            self.name_table_widget.setItem(row, 1, QTableWidgetItem(name))
            self.name_table_widget.setItem(row, 2, QTableWidgetItem(',  '.join(lists)))
            self.name_table_widget.setCellWidget(row, 0, checkbox)

    def toggle_all(self, checked):
        for checkbox in self.checkboxes:
            checkbox.setChecked(checked)
