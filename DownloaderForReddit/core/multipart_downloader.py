import os
import requests
import asyncio
import logging

from .runner import Runner, verify_run


CHUNK_SIZE = 1024 * 1024


class MultipartDownloader(Runner):

    def __init__(self, executor, stop_run):
        super().__init__(stop_run)
        self.logger = logging.getLogger(f'DownloaderForReddit.{__name__}')
        self.executor = executor
        self.part_count = 0
        self.failed_parts = 0

    def run(self, url, path, size):
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(self.download(url, path, size))
        except:
            self.logger.error('Multi-part download failed', extra={'url': url, 'path': path}, exc_info=True)
        finally:
            loop.close()

    @verify_run
    async def download(self, url, path, file_size):
        loop = asyncio.get_event_loop()
        chunks = range(0, file_size, CHUNK_SIZE)
        self.part_count = len(chunks)
        tasks = [
            loop.run_in_executor(
                self.executor,
                self.download_part,
                url,
                start,
                start + CHUNK_SIZE - 1,
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
    def download_part(self, url, start, end, path):
        retry = True
        tries = 0

        def download():
            headers = {'Range': f'bytes={start}-{end}'}
            response = requests.get(url, headers=headers, stream=True, timeout=10)
            if response.status_code == 206:
                with open(path, 'wb') as file:
                    for chunk in response.iter_content(CHUNK_SIZE):
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

    def log_part_error(self, message, extra=None, exc_info=True, log=True):
        if log:
            self.failed_parts += 1
            if self.failed_parts <= 3:
                self.logger.error(message, extra=extra, exc_info=exc_info)
            else:
                self.logger.error('Failed to download multiple chunks of multi-part download.  '
                                  'No further errors will be logged for this download',
                                  extra=extra, exc_info=exc_info)
