from Extractors.Extractor import Extractor


class DirectExtractor(Extractor):

    extensions = ('.jpg', '.jpeg', '.png', '.gif', '.gifv', '.mp4', '.webm', '.wmv')

    def __init__(self, url, user, post_title, subreddit, creation_date, subreddit_save_method, name_downloads_by,
                 save_path, content_display_only):
        super().__init__(url, user, post_title, subreddit, creation_date, subreddit_save_method, name_downloads_by,
                         save_path, content_display_only)

    def extract_content(self):
        domain, id_with_ext = self.url.rsplit('/', 1)
        image_id, extension = id_with_ext.rsplit('.', 1)
        file_name = self.post_title if self.name_downloads_by == 'Post Title' else image_id
        self.make_content(self.url, file_name, extension)