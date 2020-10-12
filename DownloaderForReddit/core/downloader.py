import os
import requests
import logging
from concurrent.futures import ThreadPoolExecutor

from .runner import Runner, verify_run
from .multipart_downloader import MultipartDownloader
from .errors import Error
from ..utils import injector, system_util
from ..database import Content
from ..messaging.message import Message


class Downloader(Runner):

    """
    Class that is responsible for the actual downloading of content.
    """

    def __init__(self, download_queue, download_session_id, stop_run):
        """
        Initializes the Downloader class.
        :param download_queue: A queue of Content items that are to be downloaded.
        :type download_queue: Queue
        """
        super().__init__(stop_run)
        self.logger = logging.getLogger(__name__)
        self.download_queue = download_queue  # contains the id of content created elsewhere that is to be downloaded
        self.download_session_id = download_session_id
        self.output_queue = injector.get_message_queue()
        self.db = injector.get_database_handler()
        self.settings_manager = injector.get_settings_manager()

        self.thread_count = self.settings_manager.download_thread_count
        self.executor = ThreadPoolExecutor(self.thread_count)
        self.multi_part_executor = ThreadPoolExecutor(8)
        self.futures = []
        self.hold = False
        self.hard_stop = False
        self.download_count = 0

    @property
    def running(self):
        if self.hold:
            return len(self.futures) > 0
        return True

    def run(self):
        """
        Removes content from the queue and sends it to the thread pool executor for download until it is told to stop.
        """
        self.logger.debug('Downloader running')
        while self.continue_run:
            item = self.download_queue.get()
            if item is not None:
                if item == 'HOLD':
                    self.hold = True
                elif item == 'RELEASE_HOLD':
                    self.hold = False
                else:
                    future = self.executor.submit(self.download, content_id=item)
                    future.add_done_callback(self.remove_future)
                    self.futures.append(future)
            else:
                break
        self.executor.shutdown(wait=True)
        self.logger.debug('Downloader exiting')

    def remove_future(self, future):
        self.futures.remove(future)

    @verify_run
    def download(self, content_id: int):
        """
        Connects to the content url and downloads the content item to the file path specified by the content item.
        :param content_id: The id of the content item which is to be queried from the database, then downloaded.
        """
        try:
            with self.db.get_scoped_session() as session:
                content = session.query(Content).get(content_id)
                response = requests.get(content.url, stream=True, timeout=10)
                if response.status_code == 200:
                    file_size = int(response.headers['Content-Length'])
                    self.check_file_path(content)
                    file_path = content.get_full_file_path()
                    if self.settings_manager.use_multi_part_downloader and \
                            file_size > self.settings_manager.multi_part_threshold:
                        multi_part_downloader = MultipartDownloader(self.stop_run)
                        multi_part_downloader.run(content.url, file_path, file_size)
                        self.finish_multi_part_download(content, multi_part_downloader)
                    else:
                        with open(file_path, 'wb') as file:
                            for chunk in response.iter_content(1024 * 1024):
                                if not self.hard_stop:
                                    file.write(chunk)
                                else:
                                    break
                        self.finish_download(content)
                else:
                    self.handle_unsuccessful_response(content, response.status_code)
        except ConnectionError:
            self.handle_connection_error(content)
        except:
            self.handle_unknown_error(content)

    def check_file_path(self, content: Content):
        """
        Checks the content's full file path to make sure there are no naming conflicts.  If there are, a number is
        incremented and appended to the contents title until a naming conflict no longer exists.
        :param content: The Content item who's path is to be checked.
        """
        try:
            system_util.create_directory(content.directory_path)
        except PermissionError:
            self.logger.error('Could not create directory path', extra={'directory_path': content.directory_path},
                              exc_info=True)
        unique_count = 1
        clean_title = system_util.clean(content.title)
        download_title = clean_title
        path = content.get_full_file_path(download_title)
        while os.path.exists(path):
            download_title = f'{clean_title}({unique_count})'
            path = content.get_full_file_path(download_title)
            unique_count += 1
        content.download_title = download_title

    def finish_download(self, content: Content):
        """
        Wraps up loose ends from the download process.  Takes care of updating the user about the download status,
        setting the date modified for the file, and saving the content changes to the database.
        :param content: The content item that has been downloaded and needs to be finished.
        """
        if not self.hard_stop:
            if self.settings_manager.match_file_modified_to_post_date:
                system_util.set_file_modify_time(content.get_full_file_path(), content.post.date_posted.timestamp())
            content.set_downloaded(self.download_session_id)
            self.download_count += 1
            if self.settings_manager.output_saved_content_full_path:
                Message.send_debug(f'Saved: {content.get_full_file_path()}')
            else:
                Message.send_debug(f'Saved: {content.user.name}: {content.title}')
        else:
            message = 'Download was stopped before finished'
            content.set_download_error(Error.DOWNLOAD_STOPPED, message)
            Message.send_download_error(f'{message}. File at path: "{content.get_full_file_path()}" may be corrupted')

    def finish_multi_part_download(self, content: Content, multipart_downloader: MultipartDownloader):
        parts = multipart_downloader.part_count
        failed = multipart_downloader.failed_parts
        if failed > 0:
            failed_percent = round((failed / parts) * 100)
            content.set_download_error(Error.MULTIPART_FAILURE,
                                       f'{failed_percent}% of multi-part download parts failed to download')
        else:
            self.finish_download(content)

    def handle_unsuccessful_response(self, content: Content, status_code):
        message = 'Failed Download: Unsuccessful response from server'
        self.log_errors(content, message, status_code=status_code)
        self.output_error(content, message)
        content.set_download_error(Error.UNSUCCESSFUL_RESPONSE, f'{message}: status_code: {status_code}')

    def handle_connection_error(self, content: Content):
        message = 'Failed Download: Failed to establish download connection'
        self.log_errors(content, message)
        self.output_error(content, message)
        content.set_download_error(Error.CONNECTION_ERROR, message)

    def handle_unknown_error(self, content: Content):
        message = 'An unknown error occurred during download'
        self.log_errors(content, message)
        self.output_error(content, message)
        content.set_download_error(Error.UNKNOWN_ERROR, message)

    def log_errors(self, content: Content, message, **kwargs):
        extra = {
            'url': content.url,
            'title': content.title,
            'submission_id': content.post.reddit_id,
            'user': content.user,
            'subreddit': content.subreddit,
            'save_path': content.get_full_file_path(),
            **kwargs
        }
        self.logger.error(message, extra=extra, exc_info=True)

    def output_error(self, content, message):
        output_append = f'\nPost: {content.post.title}\nUrl: {content.url}\nUser: {content.user}\n' \
                        f'Subreddit: {content.subreddit}\n'
        Message.send_download_error(message + output_append)
