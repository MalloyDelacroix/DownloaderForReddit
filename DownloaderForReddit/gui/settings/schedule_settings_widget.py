import time
from PyQt5.QtWidgets import QListWidgetItem, QCheckBox, QWidget, QLabel, QVBoxLayout, QFrame, QMenu
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor

from .abstract_settings_widget import AbstractSettingsWidget
from DownloaderForReddit.guiresources.settings.schedule_settings_widget_auto import Ui_ScheduleSettingsWidget
from DownloaderForReddit.utils import injector
from DownloaderForReddit.scheduling.tasks import DownloadTask, Interval
from DownloaderForReddit.database.models import RedditObjectList


class ScheduleSettingsWidget(AbstractSettingsWidget, Ui_ScheduleSettingsWidget):

    def __init__(self):
        super().__init__()
        self.scheduler = injector.get_scheduler()
        self.db = injector.get_database_handler()
        self.task_map = {}
        self.new_tasks = []
        self.deleted_tasks = []
        self.load_ui()
        self.schedule_download_button.clicked.connect(self.add_task)

        self.scheduled_downloads_list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.scheduled_downloads_list_widget.customContextMenuRequested.connect(self.task_list_widget_context_menu)

    def load_ui(self):
        self.error_label.setVisible(False)
        for interval in Interval:
            # This is a patch to fix an issue that has otherwise been resolved.  WEEK is not available and should  be
            # removed in future versions.  This allows us to keep the WEEK enum so that any existing erroneous tasks
            # with the WEEK interval can be loaded from the database, but new tasks with the WEEK interval cannot be
            # added.
            if interval.name != 'WEEK':
                self.interval_combo.addItem(interval.name.title(), interval)
        self.interval_combo.setCurrentIndex(-1)
        self.user_list_combo.addItem('None', None)
        self.subreddit_list_combo.addItem('None', None)
        with self.db.get_scoped_session() as session:
            for user_list in session.query(RedditObjectList).filter(RedditObjectList.list_type == 'USER'):
                self.user_list_combo.addItem(user_list.name, user_list)
            for sub_list in session.query(RedditObjectList).filter(RedditObjectList.list_type == 'SUBREDDIT'):
                self.subreddit_list_combo.addItem(sub_list.name, sub_list)

    @property
    def description(self):
        return 'Schedule downloads to run at a certain time and/or interval'

    def load_settings(self):
        self.perpetual_download_checkbox.setChecked(self.settings.perpetual_download)
        with self.db.get_scoped_session() as session:
            for task in session.query(DownloadTask):
                self.add_task_to_list(task)

    def apply_settings(self):
        self.settings.perpetual_download = self.perpetual_download_checkbox.isChecked()
        self.check_modified()
        for task in self.new_tasks:
            self.scheduler.add_task(task)
        for task in self.deleted_tasks:
            self.scheduler.remove_task(task.id)
        self.new_tasks.clear()
        self.deleted_tasks.clear()

    def check_modified(self):
        with self.db.get_scoped_session() as session:
            for task in self.task_map.values():
                if task not in self.new_tasks and task not in self.deleted_tasks:
                    if session.is_modified(task):
                        session.add(task)
                        if task.active:
                            self.scheduler.schedule_task(task)
                        else:
                            self.scheduler.pause_task(task)
            session.commit()

    def add_task(self):
        if self.check_value_entry():
            self.error_label.setVisible(False)
            task = DownloadTask(
                interval=self.interval_combo.currentData(Qt.UserRole),
                value=self.interval_value_line_edit.text(),
                user_list=self.user_list_combo.currentData(Qt.UserRole),
                subreddit_list=self.subreddit_list_combo.currentData(Qt.UserRole),
                active=True
            )
            with self.db.get_scoped_session() as session:
                existing = session.query(DownloadTask) \
                    .filter(DownloadTask.interval == task.interval) \
                    .filter(DownloadTask.value == task.value) \
                    .filter(DownloadTask.user_list_id == task.user_list_id) \
                    .filter(DownloadTask.subreddit_list_id == task.subreddit_list_id) \
                    .scalar()
                if existing is None:
                    self.add_task_to_list(task)
                    self.new_tasks.append(task)
                    self.clear_input()
                else:
                    self.error_label.setText('Matching download schedule already exists')
                    self.error_label.setVisible(True)

    def check_value_entry(self):
        if self.check_value_format():
            return True
        else:
            self.error_label.setText('Invalid value entered')
            self.error_label.setVisible(True)
            return False

    def check_value_format(self):
        text = self.interval_value_line_edit.text()
        interval = self.interval_combo.currentData(Qt.UserRole)
        if interval == Interval.MINUTE:
            try:
                time.strptime(text, ':%S')
                return True
            except ValueError:
                return False
        elif interval == Interval.HOUR:
            try:
                time.strptime(text, '%M:%S')
                return True
            except ValueError:
                return False
        else:
            try:
                if len(text.split(':')[0]) == 1:
                    text = '0' + text
                if text.count(':') == 1:
                    text += ':00'
                time.strptime(text, '%H:%M:%S')
                self.interval_value_line_edit.setText(text)
                return True
            except ValueError:
                return False

    def add_task_to_list(self, task):
        item = QListWidgetItem()
        setattr(item, 'tag', task.tag)
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel(task.display))
        layout.addWidget(QLabel(f'User List: {task.user_list_display}'))
        layout.addWidget(QLabel(f'Sub List: {task.subreddit_list_display}'))
        checkbox = QCheckBox('active')
        checkbox.setChecked(task.active)
        checkbox.toggled.connect(lambda: setattr(task, 'active', checkbox.isChecked()))
        layout.addWidget(checkbox)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        layout.addWidget(line)
        widget.setLayout(layout)

        item.setSizeHint(widget.sizeHint())
        self.scheduled_downloads_list_widget.addItem(item)
        self.scheduled_downloads_list_widget.setItemWidget(item, widget)
        self.task_map[task.tag] = task

    def clear_input(self):
        self.interval_combo.setCurrentIndex(-1)
        self.interval_value_line_edit.clear()
        self.user_list_combo.setCurrentIndex(0)
        self.subreddit_list_combo.setCurrentIndex(0)

    def task_list_widget_context_menu(self):
        menu = QMenu()
        menu.addAction('Remove Task', lambda: self.remove_task(self.scheduled_downloads_list_widget.currentRow()))
        menu.exec_(QCursor.pos())

    def remove_task(self, row):
        item = self.scheduled_downloads_list_widget.takeItem(row)
        task = self.task_map[item.tag]
        if task not in self.new_tasks:
            self.deleted_tasks.append(task)
        else:
            self.new_tasks.remove(task)
