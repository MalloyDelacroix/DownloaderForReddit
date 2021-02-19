from datetime import datetime
from threading import Event
import schedule
from PyQt5.QtCore import QObject, pyqtSignal

from .tasks import DownloadTask, Interval
from ..utils import injector, system_util


class Scheduler(QObject):

    run_task = pyqtSignal(tuple)
    countdown = pyqtSignal(object)
    finished = pyqtSignal()

    exit = Event()

    def __init__(self):
        super().__init__()
        self.db = injector.get_database_handler()
        self.continue_run = True
        self.update_countdown = True
        self.load_tasks()

    def load_tasks(self):
        with self.db.get_scoped_session() as session:
            for task in session.query(DownloadTask):
                if task.active:
                    self.schedule_task(task)

    def run(self):
        while not self.exit.is_set():
            schedule.run_pending()
            self.calculate_countdown()
            self.exit.wait(0.999)
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
                if task.active:
                    self.schedule_task(task)

    def schedule_task(self, task):
        base = schedule.every()
        n = getattr(base, task.interval.unit)
        if task.interval != Interval.SECOND:
            n = n.at(task.value)
        n.do(self.launch_task, user_list_id=task.user_list_id, subreddit_list_id=task.subreddit_list_id).tag(task.tag)
        self.update_countdown = True

    def pause_task(self, task):
        schedule.clear(task.tag)

    def remove_task(self, task_id):
        with self.db.get_scoped_session() as session:
            task = session.query(DownloadTask).get(task_id)
            schedule.clear(task.tag)
            session.delete(task)
            session.commit()

    def launch_task(self, user_list_id, subreddit_list_id):
        self.run_task.emit((user_list_id, subreddit_list_id))

    def stop_run(self):
        self.exit.set()

    def calculate_countdown(self):
        """
        Calculates when the next scheduled download will begin and sends the update signal if there is one scheduled.
        """
        if self.update_countdown:
            next_run = schedule.next_run()
            if next_run is not None:
                t = next_run - datetime.now()
                dur = system_util.format_time_delta(t)
                self.countdown.emit(dur)
            else:
                self.countdown.emit(None)
                self.update_countdown = False
