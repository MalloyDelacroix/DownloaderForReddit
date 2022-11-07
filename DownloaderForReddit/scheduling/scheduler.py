import logging
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
        self.logger = logging.getLogger(__name__)
        self.db = injector.get_database_handler()
        self.continue_run = True
        self.update_countdown = True
        self.load_tasks()

    def load_tasks(self):
        """
        Loads stored download tasks from the database and schedules them with the scheduling module.
        """
        with self.db.get_scoped_session() as session:
            for task in session.query(DownloadTask):
                if task.active:
                    try:
                        self.schedule_task(task)
                    except (schedule.ScheduleValueError, schedule.ScheduleError):
                        # If the task cannot be loaded, remove it from the database
                        self.remove_task(task.id)

    def run(self):
        while not self.exit.is_set():
            schedule.run_pending()
            self.calculate_countdown()
            self.exit.wait(0.999)
        self.finished.emit()

    def add_task(self, task):
        """
        Checks the database to ensure that the supplied task does not already exist.  If it does not already exist, an
        attempt is made to schedule the task.  If scheduling the task fails, the task is then only committed to the
        database if scheduling the task is successful.
        :param task: A task model instance that is to be scheduled and added to the database.
        :type task DownloadTask
        """
        with self.db.get_scoped_session() as session:
            existing = session.query(DownloadTask)\
                .filter(DownloadTask.interval == task.interval)\
                .filter(DownloadTask.value == task.value)\
                .filter(DownloadTask.user_list_id == task.user_list_id)\
                .filter(DownloadTask.subreddit_list_id == task.subreddit_list_id)\
                .scalar()
            if existing is None:
                try:
                    if task.active:
                        self.schedule_task(task)
                    session.add(task)
                    session.commit()
                except (schedule.ScheduleValueError, schedule.ScheduleError):
                    # Do not commit the task to the database if there was an error scheduling the task
                    pass

    def schedule_task(self, task):
        """
        Attempts to schedule the task with the scheduling module.
        :param task: A task model instance that will schedule with the scheduling module.
        :type task DownloadTask
        """
        try:
            base = schedule.every()
            n = getattr(base, task.interval.unit)
            if task.interval != Interval.SECOND:
                n = n.at(task.value)
            n.do(self.launch_task, user_list_id=task.user_list_id, subreddit_list_id=task.subreddit_list_id).tag(task.tag)
            self.update_countdown = True
        except Exception as e:
            # Log the error no matter what it is, then raise the exception and let the caller handle it as necessary
            self.logger.error('Failed to schedule task', extra={'task': task.display}, exc_info=True)
            raise e

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
