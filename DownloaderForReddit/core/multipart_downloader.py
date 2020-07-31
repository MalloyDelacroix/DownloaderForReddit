import os
import requests
import asyncio
import logging


CHUNK_SIZE = 1024 * 1024


class MultipartDownloader:

    def __init__(self, executor):
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

    async def get_size(self, url):
        response = requests.get(url, stream=True, timeout=10)
        size = int(response.headers['Content-Length'])
        return size

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
                chunk_path = f'{path}.part{x}'
                with open(chunk_path, 'rb') as part_file:
                    file.write(part_file.read())
                os.remove(chunk_path)

    def download_part(self, url, start, end, path):
        headers = {'Range': f'bytes={start}-{end}'}
        response = requests.get(url, headers=headers, stream=True, timeout=10)
        if response.status_code == 206:
            with open(path, 'wb') as file:
                for chunk in response.iter_content(CHUNK_SIZE):
                    file.write(chunk)
        else:
            self.failed_parts += 1
            if self.failed_parts <= 3:
                self.logger.error('Failed to download chunk of muli-part download - bad response',
                                  extra={'status_code': response.status_code})
            else:
                self.logger.error('Failed to download multiple chunks of multi-part download.  '
                                  'No further errors will be logged for this download',
                                  extra={'status_code': response.status_code})
