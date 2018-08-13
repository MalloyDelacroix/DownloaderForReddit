

class MockSettingsManager:

    def __init__(self):
        self.save_failed_extracts = True
        self.save_undownloaded_content = True
        self.max_download_thread_count = 4

        self.restrict_by_score = False
        self.score_limit_operator = 'GREATER'
        self.post_score_limit = 3000

        self.post_limit = 25

        self.restrict_by_date = False
        self.restrict_by_custom_date = False
        self.custom_date = 86400

        self.download_images = True
        self.download_videos = True
        self.avoid_duplicates = True

