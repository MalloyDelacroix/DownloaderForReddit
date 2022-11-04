import redgifs

from .base_extractor import BaseExtractor
from ..core.errors import Error
from ..core.download import HEADERS


class RedgifsExtractor(BaseExtractor):

    url_key = ['redgifs']

    def __init__(self, post, **kwargs):
        """
        An extractor class that interacts exclusively with the redgifs website.
        """
        super().__init__(post, **kwargs)
    #     self.api_endpoint = 'https://api.redgifs.com/v2/gifs/'
    #
    # def extract_content(self):
    #     try:
    #         if self.url.lower().endswith(const.ANIMATED_EXT):
    #             self.extract_direct_link()
    #         else:
    #             self.extract_single()
    #     except:
    #         message = 'Failed to locate content'
    #         self.handle_failed_extract(error=Error.FAILED_TO_LOCATE, message=message, extractor_error_message=message)
    #
    # def extract_single(self):
    #     gif_id = self.url.rsplit('/', 1)[-1]
    #     url = self.api_endpoint + gif_id
    #     data = self.get_json(url)
    #     if not data:
    #         return
    #     download_url = self.get_download_url(data)
    #     if not download_url:
    #         message = 'Failed to locate an appropriate download url in the host response data'
    #         self.handle_failed_extract(error=Error.FAILED_TO_LOCATE, message=message, extraction_error_message=message)
    #     self.make_content(download_url, 'mp4', media_id=gif_id)
    #
    # @staticmethod
    # def get_download_url(data):
    #     urls = data['gif']['urls']
    #     try:
    #         return urls['hd']
    #     except KeyError:
    #         return urls.get('sd', None)

    def extract_content(self):
        try:
            api = redgifs.API()
            api.login()
            response = api.get_gif(self.get_gif_id())
            url = self.get_download_url(response)
            content = self.make_content(url, 'mp4')
            HEADERS[content.id] = api.http.headers
        except:
            message = 'Failed to extract content from redgifs'
            self.handle_failed_extract(error=Error.FAILED_TO_LOCATE, message=message, exetractor_error_message=message)

    def get_gif_id(self):
        return self.url.rsplit('/', 1)[-1]

    @staticmethod
    def get_download_url(data):
        try:
            return data.urls.hd
        except KeyError:
            return data.urls.sd

    # def extract_with_yt_dlp(self):
    #     """
    #     This method is out of date at the moment.  But with the way redgifs is changing their api, it could very well
    #     be relevant again soon.  So this is staying here, just in case.
    #     """
    #     try:
    #         with YoutubeDL({'format': 'mp4'}) as ydl:
    #             result = ydl.extract_info(self.url, download=False)
    #             content = self.make_content(result['url'], 'mp4')
    #             HEADERS[content.id] = result['http_headers']
    #     except:
    #         message = 'Failed to locate content'
    #         self.handle_failed_extract(error=Error.FAILED_TO_LOCATE, message=message, extractor_error_message=message)
