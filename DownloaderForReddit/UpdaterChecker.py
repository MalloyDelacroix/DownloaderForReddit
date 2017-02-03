import requests
import shutil
import os


class UpdateChecker:

    def __init__(self, installed_version):
        self.installed_version = installed_version
        self.release_api_caller = 'https://api.github.com/repos/MalloyDelacroix/DownloaderForReddit/releases/latest'
        self.newest_version = None
        self._json = None

    def retrieve_json_data(self):
        response = requests.get(self.release_api_caller)
        if response.status_code == 200:
            self._json = response.json()

    def check_releases(self):
        if self._json['tag_name'] != self.installed_version:
            pass
            # Call another function to start a separate installer application




"""
Test work:

def download_latest_release():
    api = 'https://api.github.com/'
    response = requests.get(api + 'repos/MalloyDelacroix/DownloaderForReddit/releases/latest')

    if response.status_code == 200:
        r = response.json()
        version = r['tag_name']
        id = r['id']
        assets_list = r['assets']
        print(id)
        print(version)
        print('\nasset:\n')

        for x in assets_list:
            if x['content_type'] == 'application/x-compressed':
                print('New Download')
                download_url = x['browser_download_url']
                filename = 'C:path_to_folder/%s' % x['name']
                download = requests.get(download_url, stream=True)
                if download.status_code == 200:
                    with open(filename, 'wb') as file:
                        for chunk in download.iter_content(1024):
                            file.write(chunk)
                    print('download complete')

"""




