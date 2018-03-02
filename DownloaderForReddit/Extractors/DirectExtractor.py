from Extractors.BaseExtractor import BaseExtractor


class DirectExtractor(BaseExtractor):

    url_key = None

    def __init__(self, post, reddit_object, content_display_only=False):
        super().__init__(post, reddit_object, content_display_only)

    def extract_content(self):
        domain, id_with_ext = self.url.rsplit('/', 1)
        image_id, extension = id_with_ext.rsplit('.', 1)
        file_name = self.post_title if self.name_downloads_by == 'Post Title' else image_id
        self.make_content(self.url, file_name, extension)
