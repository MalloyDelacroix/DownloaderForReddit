import schedule
import time
from PyQt5.QtCore import QObject, pyqtSignal

from .tasks import DownloadTask, Interval
from ..utils import injector


class Scheduler(QObject):

    run_task = pyqtSignal(tuple)
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.db = injector.get_database_handler()
        self.continue_run = True
        self.load_tasks()

    def load_tasks(self):
        with self.db.get_scoped_session() as session:
            for task in session.query(DownloadTask):
                self.schedule_task(task)

    def run(self):
        while self.continue_run:
            schedule.run_pending()
            time.sleep(0.5)
        self.finished.emit()

    def add_task(self, task):
        with self.db.get_scoped_session() as session:
            existing = session.query(DownloadTask)\
                .filter(DownloadTask.interval == task.interval)\
                .filter(DownloadTask.value == task.value)\
                .filter(DownloadTask.user_list_id == task.user_list_id)\
                .filter(DownloadTask.subreddit_list_id == task.subreddit_list_id)\
                .scalar()
            if existing is None:
                session.add(task)
                session.commit()
                self.schedule_task(task)

    def schedule_task(self, task):
        base = schedule.every()
        n = getattr(base, task.interval.unit)
        if task.interval != Interval.SECOND:
            n = n.at(task.value)
        n.do(self.launch_task, user_list_id=task.user_list_id, subreddit_list_id=task.subreddit_list_id).tag(task.tag)

    def remove_task(self, task_id):
        with self.db.get_scoped_session() as session:
            task = session.query(DownloadTask).get(task_id)
            schedule.clear(task.tag)
            task.delete()
            session.commit()

    def launch_task(self, user_list_id, subreddit_list_id):
        print('emitting signal')
        self.run_task.emit((user_list_id, subreddit_list_id))

    def stop_run(self):
        self.continue_run = False
