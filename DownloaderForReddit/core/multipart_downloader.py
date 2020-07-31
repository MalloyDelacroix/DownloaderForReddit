import os
import requests
import asyncio


CHUNK_SIZE = 1024 * 1024


class MultipartDownloader:

    def __init__(self, executor):
        self.executor = executor

    def run(self, url, path, size):
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(self.download(url, path, size))
        except:
            print('Multi-part download failed')
        finally:
            loop.close()
            print(f'\nClosing loop for {path}\n')

    async def get_size(self, url):
        response = requests.get(url, stream=True, timeout=10)
        size = int(response.headers['Content-Length'])
        return size

    async def download(self, url, path, file_size):
        print(f'\nDownloading url: {url}\nPath: {path}\n')
        loop = asyncio.get_event_loop()
        chunks = range(0, file_size, CHUNK_SIZE)
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
            for x in range(len(chunks)):
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
