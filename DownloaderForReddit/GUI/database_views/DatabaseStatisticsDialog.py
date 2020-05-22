from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QFormLayout
from sqlalchemy.sql import func
from sqlalchemy import desc

from DownloaderForReddit.Database.Models import DownloadSession, RedditObject, User, Subreddit, Post, Content, Comment
from DownloaderForReddit.Utils import Injector


class DatabaseStatisticsDialog(QDialog):

    def __init__(self):
        QDialog.__init__(self)
        self.db = Injector.get_database_handler()
        with self.db.get_scoped_session() as session:
            user_count_sub = session.query(Post.significant_reddit_object_id, func.count(Post.id).label('count')) \
                .group_by(Post.significant_reddit_object_id).subquery()
            user_count = session.query(User, 'count')\
                .outerjoin(user_count_sub, user_count_sub.c.significant_reddit_object_id == User.id)\
                .order_by(desc('count')).first()
            sub_count_sub = session.query(Post.significant_reddit_object_id, func.count(Post.id).label('count')) \
                .group_by(Post.significant_reddit_object_id).subquery()
            sub_count = session.query(Subreddit, 'count') \
                .outerjoin(sub_count_sub, sub_count_sub.c.significant_reddit_object_id == Subreddit.id) \
                .order_by(desc('count')).first()
            self.reddit_object_map = {
                'Total Reddit Objects': session.query(RedditObject.id).count(),
                'Total Users': session.query(User.id).count(),
                'Total Subreddits': session.query(Subreddit.id).count(),
                'Total Significant Reddit Objects':
                    session.query(RedditObject.id).filter(RedditObject.significant == True).count(),
                'Total Significant Users': session.query(User.id).filter(User.significant == True).count(),
                'Total Significant Subreddits':
                    session.query(Subreddit.id).filter(Subreddit.significant == True).count(),
                'User With Most Posts': user_count.name,
                'User Post Count': user_count.count,
                'Subreddit With Most Posts': sub_count.name,
                'Subreddit Post Count': sub_count.count,

            }

            post_count = session.query(Post.id).count()
            nsfw_post_count = session.query(Post.id).filter(Post.nsfw == True).count()
            self_post_count = session.query(Post.id).filter(Post.is_self == True).count()
            common_title_query = session.query(func.count(Post.id).label('count'), Post.title.label('title'))\
                .group_by(Post.title).order_by(desc('count')).first()
            domain_query = session.query(func.count(Post.id).label('count'), Post.domain.label('domain'))\
                .group_by(Post.domain).order_by(desc('count')).first()
            error_query = session.query(func.count(Post.id).label('count'), Post.extraction_error.label('error'))\
                .group_by(Post.extraction_error).order_by(desc('count')).first()
            self.post_map = {
                'Total Posts': post_count,
                'Total Extracted Posts': session.query(Post.id).filter(Post.extracted == True).count(),
                'Total Failed Posts': session.query(Post.id).filter(Post.extraction_error != None).count(),
                'Total NSFW Posts': nsfw_post_count,
                'Total Non-NSFW Posts': session.query(Post.id).filter(Post.nsfw == False).count(),
                'Percentage of NSFW Posts': round((nsfw_post_count / post_count) * 100, 2),
                'Number of Self Posts': self_post_count,
                'Percentage of Self Posts': round((self_post_count / post_count) * 100, 2),
                'Highest Score': session.query(func.max(Post.score)).first()[0],
                'Lowest Score': session.query(func.min(Post.score)).first()[0],
                'Average Score': round(session.query(func.avg(Post.score)).first()[0]),
                'Most Common Title': common_title_query.title,
                'Times Title Used': common_title_query.count,
                'Total Unique Post Domains': session.query(Post.domain).distinct().count(),
                'Most Common Domain': domain_query.domain,
                'Times Domain Used': domain_query.count,
                'Oldest Post Extraction': session.query(Post.extraction_date).order_by(Post.extraction_date).first(),
                'Newest Post Extraction': session.query(Post.extraction_date)
                    .order_by(desc(Post.extraction_date)).first(),
                'Oldest Post Date': session.query(Post.date_posted).order_by(Post.date_posted).first(),
                'Newest Post Date': session.query(Post.date_posted).order_by(desc(Post.date_posted)).first(),
                'Most Common Error': error_query.error,
                'Times Error Encountered': error_query.count,

            }

        self.setup_ui()

    def setup_ui(self):
        self.setup_reddit_object_ui()

    def setup_reddit_object_ui(self):
        layout = QFormLayout()
        for key, value in self.reddit_object_map:
            if type(value) == int:
                value = self.output_number(value)
            layout.addRow(QLabel(key), QLabel(value))

    def output_number(self, number):
        return '{:,}'.format(number)
