import os
import requests
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

from . import HEADERS
from DownloaderForReddit.core.runner import Runner, verify_run
from DownloaderForReddit.utils import injector


class MultipartDownloader(Runner):

    def __init__(self, stop_run):
        super().__init__(stop_run)
        self.logger = logging.getLogger(__name__)
        self.settings_manager = injector.get_settings_manager()
        self.executor = ThreadPoolExecutor(self.settings_manager.multi_part_thread_count)
        self.chunk_size = self.settings_manager.multi_part_chunk_size
        self.part_count = 0
        self.failed_parts = 0

    def run(self, content, path, size):
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(self.download(content, path, size))
        except:
            self.logger.error('Multi-part download failed', extra={'url': content.url, 'path': path}, exc_info=True)
        finally:
            loop.close()

    @verify_run
    async def download(self, content, path, file_size):
        loop = asyncio.get_event_loop()
        chunks = range(0, file_size, self.chunk_size)
        self.part_count = len(chunks)
        tasks = [
            loop.run_in_executor(
                self.executor,
                self.download_part,
                content,
                start,
                start + self.chunk_size - 1,
                f'{path}.part{x}'
            )
            for x, start in enumerate(chunks)
        ]
        await asyncio.wait(tasks)

        with open(path, 'wb') as file:
            for x in range(self.part_count):
                try:
                    chunk_path = f'{path}.part{x}'
                    with open(chunk_path, 'rb') as part_file:
                        file.write(part_file.read())
                    os.remove(chunk_path)
                except FileNotFoundError:
                    self.logger.error('Failed to join multi-download part into complete file',
                                      extra={'chunk_path': chunk_path}, exc_info=True)

    @verify_run
    def download_part(self, content, start, end, path):
        retry = True
        tries = 0
        url = content.url

        def download():
            headers = self.get_headers(content, start, end)
            response = requests.get(url, headers=headers, stream=True, timeout=10)
            if response.status_code == 206:
                with open(path, 'wb') as file:
                    for chunk in response.iter_content(self.chunk_size):
                        file.write(chunk)
                return True
            else:
                self.log_part_error('Failed to download chunk of muli-part download - bad response',
                                    extra={'status_code': response.status_code}, exc_info=False)
                return False

        while self.continue_run and retry and tries < 3:
            tries += 1
            try:
                success = download()
                if success:
                    retry = False
            except requests.exceptions.ConnectTimeout:
                self.log_part_error('Operation timed out before establishing a connection to the server',
                                    extra={'url': url, 'range': f'{start} - {end}'}, log=tries >= 3)
            except requests.exceptions.ReadTimeout:
                self.log_part_error('Connection timed out while reading data from server',
                                    extra={'url': url, 'range': f'{start} - {end}'}, log=tries >= 3)
            except requests.exceptions.ChunkedEncodingError:
                self.log_part_error('Connection experienced a chunk encoding error and closed before complete',
                                    extra={'url': url, 'range': f'{start} - {end}'}, log=tries >= 3)
            except:
                self.log_part_error('Unknown error occurred', extra={'url': url, 'range': f'{start} - {end}'},
                                    log=tries >= 3)

    def get_headers(self, content, start, end):
        headers = {'Range': f'bytes={start}-{end}'}
        download_headers = HEADERS.get(content.id, None)
        if download_headers is not None:
            headers.update(download_headers)
        return headers

    def log_part_error(self, message, extra=None, exc_info=True, log=True):
        if log:
            self.failed_parts += 1
            if self.failed_parts <= 3:
                self.logger.error(message, extra=extra, exc_info=exc_info)
            else:
                self.logger.error('Failed to download multiple chunks of multi-part download.  '
                                  'No further errors will be logged for this download',
                                  extra=extra, exc_info=exc_info)
