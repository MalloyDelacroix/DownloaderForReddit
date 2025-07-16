import hashlib
import logging
from concurrent.futures import ThreadPoolExecutor
import requests

from DownloaderForReddit.core.runner import Runner, verify_run
from .multipart_downloader import MultipartDownloader
from . import HEADERS
from DownloaderForReddit.core.errors import Error
from DownloaderForReddit.utils import injector, system_util, general_utils
from DownloaderForReddit.database import Content
from DownloaderForReddit.messaging.message import Message
from ..duplicate_handler import DuplicateHandler


class Downloader(Runner):

    """
    The class that is responsible for the actual downloading of content.
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
        self.executor = None
        self.multi_part_executor = ThreadPoolExecutor(8)
        self.futures = []
        self.hold = False
        self.hard_stop = False
        self.download_count = 0
        self.duplicate_count = 0

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
        self.make_executor()
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
        HEADERS.clear()
        self.logger.debug('Downloader exiting')

    def make_executor(self) -> None:
        """
        Initializes a thread pool executor with the number of threads defined by the
        `thread_count` attribute in the settings manager.
        """
        self.executor = ThreadPoolExecutor(self.thread_count)

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
                content.download_title = general_utils.ensure_content_download_path(content)
                response = requests.get(content.url, stream=True, timeout=10, headers=self.check_headers(content))
                if response.status_code == 200:
                    file_size = int(response.headers['Content-Length'])
                    if file_size <= system_util.KB:
                        # If the file size is less than one KB, it is a strong indicator that the content has been
                        # deleted and what we are about to download is only a placeholder image.  So we abort download
                        self.handle_deleted_content_error(content)
                        return
                    if self.should_use_multi_part(file_size):
                        self.download_with_multipart(content, content.get_full_file_path(), file_size)
                    else:
                        if self.should_use_hash(content):
                            self.download_with_hash(content, response)
                        else:
                            self.download_without_hash(content, response)
                        self.finish_download(content)
                else:
                    self.handle_unsuccessful_response(content, response.status_code)
        except ConnectionError:
            self.handle_connection_error(content)
        except:
            self.handle_unknown_error(content)

    def check_headers(self, content):
        """
        This is a helper method to add a necessary header entry for erome downloads.  It is just a patch for a problem
        at the moment.  This can be expanded as further need arises, or replaced by a different better system.

        Checks the HEADER dict for the supplied content's id and, if found, returns the associated header data that will
        be necessary for the request to be successful.
        :param content: The content object that is in the process of being downloaded.
        :return: A dict to be used as a request header where applicable, None if there is no applicable header.
        """
        if 'erome' in content.url:
            return {"Referer": "https://www.erome.com/"}
        return HEADERS.get(content.id, None)

    def should_use_multi_part(self, file_size: int) -> bool:
        settings = self.settings_manager
        return settings.use_multi_part_downloader and file_size > settings.multi_part_threshold

    def download_with_multipart(self, content: Content, file_path: str, file_size: int) -> None:
        multi_part_downloader = MultipartDownloader(self.stop_run)
        multi_part_downloader.run(content, file_path, file_size)
        self.finish_multi_part_download(content, multi_part_downloader)

    def should_use_hash(self, content: Content) -> bool:
        sig_ro = content.post.significant_reddit_object
        return sig_ro.hash_duplicates

    def download_with_hash(self, content: Content, response: requests.Response) -> None:
        file_path = content.get_full_file_path()
        md5 = hashlib.md5()
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(1024 * 1024):
                if not self.hard_stop:
                    md5.update(chunk)
                    file.write(chunk)
                else:
                    break
        content.md5_hash = md5.hexdigest()

    def download_without_hash(self, content: Content, response: requests.Response) -> None:
        file_path = content.get_full_file_path()
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(1024 * 1024):
                if not self.hard_stop:
                    file.write(chunk)
                else:
                    break

    def finish_download(self, content: Content) -> None:
        """
        Finalizes the download process for a given content item. The method updates the content's status, manages
        duplicate detection, sets file modification times, and adjusts the download count. It also provides optional
        debugging messages indicating the download's result. If the download process was interrupted by a hard stop, it
        handles the error and logs it accordingly.

        :param content: An object representing the content being downloaded.
        """
        if not self.hard_stop:
            if content.md5_hash is not None and self.is_duplicate_content(content):
                self.handle_duplicate_content(content)
                return
            self.handle_date_modified(content)
            content.set_downloaded(self.download_session_id)
            self.download_count += 1
            self.output_downloaded_message(content)
        else:
            self.handle_download_stopped(content)

    def is_duplicate_content(self, content: Content) -> bool:
        """
        Checks if the given content's MD5 hash already exists in the database indicating a duplicate download.

        :param content: A content object with an MD5 hash to check against the database.
        :return: A boolean value indicating whether the MD5 hash exists (True) or not (False).
        """
        return DuplicateHandler.is_duplicate(content)

    def handle_duplicate_content(self, content: Content) -> None:
        """
        Handles duplicate content.

        Deletes the file associated with the given content and sends a debug message indicating that the duplicate file
        was not saved along with the content's title and URL.

        :param content: The Content instance that represents the duplicate content which was detected.
        """
        duplicate_handler = DuplicateHandler(content)
        duplicate_handler.handle_duplicate()
        if not duplicate_handler.duplicate_deleted:
            self.download_count += 1
        self.duplicate_count += 1

    def handle_date_modified(self, content: Content) -> None:
        """
        Handles updating the file's modified date to match the content's post-date if the setting is enabled.

        :param content: The content object for which the modified date is updated.
        """
        if self.settings_manager.match_file_modified_to_post_date:
            system_util.set_file_modify_time(content.get_full_file_path(), content.post.date_posted.timestamp())

    def output_downloaded_message(self, content: Content) -> None:
        """
        Outputs the download message as specified by the settings manager.

        :param content: The downloaded content object for which the message is generated.
        """
        output_data = self.get_downloaded_output_data(content)
        Message.send_debug(f'Saved: {output_data}')

    def get_downloaded_output_data(self, content: Content) -> str:
        """
        Retrieve the appropriate output data for the downloaded content based on the settings configuration.

        This method determines whether to return the full file path of the downloaded content or a formatted string
        containing the username and title. The behavior is controlled by the `output_saved_content_full_path` setting
        in the `settings_manager`.

        :param content: The content object for which the output data is generated. It contains details like the
            user's name and the content's title.
        :return: If the `output_saved_content_full_path` setting is enabled, returns the full file path of the content.
            Otherwise, returns a formatted string containing the username and the title of the content.
        """
        if self.settings_manager.output_saved_content_full_path:
            return content.get_full_file_path()
        else:
            return f'{content.user.name}: {content.title}'

    def handle_download_stopped(self, content: Content) -> None:
        """
        Handles the scenario where a download has been stopped before it could be completed. This function notifies the
        content object about the download interruption, and sends an appropriate error message indicating that the file
        may be corrupted.
        """
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
            if self.should_use_hash(content):
                self.hash_complete_multi_part_file(content)
            self.finish_download(content)

    def hash_complete_multi_part_file(self, content: Content) -> None:
        """
        Calculates and sets the MD5 hash for the full multi-part file content provided. This function updates the given
        content object with the computed hash by processing the entire file in chunks to handle large files efficiently.

        :param content: The content object containing metadata and file information that needs to be processed.
        """
        md5 = hashlib.md5()
        with open(content.get_full_file_path(), 'rb') as file:
            for chunk in iter(lambda: file.read(1024 * 1024), b''):
                md5.update(chunk)
        content.md5_hash = md5.hexdigest()

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

    def handle_deleted_content_error(self, content: Content):
        message = 'Content has been deleted'
        self.log_errors(content, message)
        self.output_error(content, message)
        content.set_download_error(Error.DOES_NOT_EXIST, message)

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
