import youtube_dl
import pkg_resources

from Extractors.BaseExtractor import BaseExtractor


class GenericVideoExtractor(BaseExtractor):

    supported_sites_file = pkg_resources.resource_filename(__name__, '../Resources/supported_video_sites.txt')
    file = open(supported_sites_file, 'r')
    url_key = [x.strip() for x in file.readlines()]
    file.close()

    def __init__(self, post, reddit_object, content_display_only=False):
        super().__init__(post, reddit_object, content_display_only)

    def extract_content(self):
        try:
            with youtube_dl.YoutubeDL({'format': 'mp4'}) as ydl:
                result = ydl.extract_info(self.url, download=False)
            if 'entries' in result:
                self.extract_playlist(result['entries'])
            else:
                self.extract_single_video(result)
        except:
            message = 'Failed to locate content'
            self.handle_failed_extract(message=message, extractor_error_message=message, failed_domain=self.domain)

    def extract_single_video(self, entry):
        self.make_content(entry['url'], self.get_filename(entry['id']), 'mp4')

    def extract_playlist(self, playlist):
        count = 1
        for entry in playlist:
            self.make_content(entry['url'], self.get_filename(entry['id']), 'mp4', count=count)
            count += 1
