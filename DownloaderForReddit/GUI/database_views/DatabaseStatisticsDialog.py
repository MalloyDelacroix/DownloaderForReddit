from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QFormLayout, QScrollArea, QWidget, QFrame
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QFont
from sqlalchemy.sql import func
from sqlalchemy import desc, extract
from datetime import datetime
import calendar

from DownloaderForReddit.Database.Models import DownloadSession, RedditObject, User, Subreddit, Post, Content, Comment
from DownloaderForReddit.Utils import Injector
from DownloaderForReddit.Core import Const


class DatabaseStatisticsDialog(QDialog):

    def __init__(self):
        QDialog.__init__(self)
        self.db = Injector.get_database_handler()
        self.settings_manager = Injector.get_settings_manager()

        geom = self.settings_manager.database_statistics_geom
        if geom is not None:
            self.resize(QSize(geom['width'], geom['height']))
            self.move(geom['x'], geom['y'])

        self.stat_widget = QWidget()
        self.stat_layout = QVBoxLayout()
        self.stat_widget.setLayout(self.stat_layout)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.stat_widget)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.scroll_area)
        self.setLayout(self.main_layout)

        with self.db.get_scoped_session() as session:
            total_reddit_objects = session.query(RedditObject.id).count()
            total_users = session.query(User.id).count()
            total_subreddits = session.query(Subreddit.id).count()
            total_significant = session.query(RedditObject.id).filter(RedditObject.significant == True).count()
            total_significant_users = session.query(User.id).filter(User.significant == True).count()
            total_significant_subreddits = session.query(Subreddit.id).filter(Subreddit.significant == True).count()

            oldest_user = session.query(User).order_by(User.date_added).first()
            newest_user = session.query(User).order_by(desc(User.date_added)).first()
            oldest_sub = session.query(Subreddit).order_by(Subreddit.date_added).first()
            newest_sub = session.query(Subreddit).order_by(desc(Subreddit.date_added)).first()

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

            user_high_score = session.query(User, func.sum(Post.score).label('score'))\
                .join(Post, Post.author_id == User.id).group_by(User.id).order_by(desc('score')).first()
            user_low_score = session.query(User, func.sum(Post.score).label('score'))\
                .join(Post, Post.author_id == User.id).group_by(User.id).order_by('score').first()

            sub_high_score = session.query(Subreddit, func.sum(Post.score).label('score'))\
                .join(Post, Post.subreddit_id == Subreddit.id).group_by(Subreddit.id).order_by(desc('score')).first()
            sub_low_score = session.query(Subreddit, func.sum(Post.score).label('score'))\
                .join(Post, Post.subreddit_id == Subreddit.id).group_by(Subreddit.id).order_by('score').first()

            user_image_query = self.get_user_extension_query(session, 'IMG')
            user_video_query = self.get_user_extension_query(session, 'VID')
            user_gif_query = self.get_user_extension_query(session, 'GIF')
            subreddit_image_query = self.get_sub_extension_query(session, 'IMG')
            subreddit_video_query = self.get_sub_extension_query(session, 'VID')
            subreddit_gif_query = self.get_sub_extension_query(session, 'GIF')

            self_post_sub = session.query(Post.significant_reddit_object_id, func.count(Post.id).label('count'))\
                .group_by(Post.significant_reddit_object_id).subquery()
            user_self_post_query = session.query(User, 'count')\
                .outerjoin(self_post_sub, self_post_sub.c.significant_reddit_object_id == User.id)\
                .order_by(desc('count')).first()
            sub_self_post_query = session.query(Subreddit, 'count')\
                .outerjoin(self_post_sub, self_post_sub.c.significant_reddit_object_id == Subreddit.id)\
                .order_by(desc('count')).first()

            comment_author_sub = session.query(Comment.author_id, func.count(Comment.id).label('count'))\
                .group_by(Comment.author_id).subquery()
            user_comment_query = session.query(User, 'count')\
                .outerjoin(comment_author_sub, comment_author_sub.c.author_id == User.id)\
                .order_by(desc('count')).first()
            comment_subreddit_sub = session.query(Comment.subreddit_id, func.count(Comment.id).label('count')) \
                .group_by(Comment.subreddit_id).subquery()
            sub_comment_query = session.query(Subreddit, 'count') \
                .outerjoin(comment_subreddit_sub, comment_subreddit_sub.c.subreddit_id == Subreddit.id) \
                .order_by(desc('count')).first()

            self.reddit_object_map = [
                ('Total Reddit Objects', total_reddit_objects),
                ('Total Users', total_users),
                ('Total Subreddits', total_subreddits),
                ('Total Significant Reddit Objects', total_significant),
                ('Total Significant Users', total_significant_users),
                ('Total Significant Subreddits', total_significant_subreddits),
                ('Total Non-Significant Reddit Objects', total_reddit_objects - total_significant),
                ('Total Non-Significant Users', total_users - total_significant_users),
                ('Total Non-Significant Subreddits', total_subreddits - total_significant_subreddits),

                ('SEPARATOR', None),
                ('Oldest User', oldest_user.name),
                ('User Added', oldest_user.date_added),
                ('Newest User', newest_user.name),
                ('User Added', newest_user.date_added),
                ('Oldest Subreddit', oldest_sub.name),
                ('Subreddit Added', oldest_sub.date_added),
                ('Newest Subreddit', newest_sub.name),
                ('Subreddit Added', newest_sub.date_added),

                ('SEPARATOR', None),
                ('User With Most Posts', user_count.User.name),
                ('Post Count', user_count.count),
                ('Subreddit With Most Posts', sub_count.Subreddit.name),
                ('Post Count', sub_count.count),

                ('SEPARATOR', None),
                ('User With Most Images', user_image_query.User.name),
                ('Image Count', user_image_query.count),
                ('User With Most Videos', user_video_query.User.name),
                ('Video Count', user_video_query.count),
                ('User With Most Gifs', user_gif_query.User.name),
                ('Gif Count', user_gif_query.count),
                ('User With Most Self Posts', user_self_post_query.User.name),
                ('Self Posts', user_self_post_query.count),
                ('User With Most Comments', user_comment_query.User.name),
                ('Comment Count', user_comment_query.count),

                ('SEPARATOR', None),
                ('Subreddit With Most Images', subreddit_image_query.Subreddit.name),
                ('Image Count', subreddit_image_query.count),
                ('Subreddit With Most Videos', subreddit_video_query.Subreddit.name),
                ('Video Count', subreddit_video_query.count),
                ('Subreddit With Most Gifs', subreddit_gif_query.Subreddit.name),
                ('Gif Count', subreddit_gif_query.count),
                ('Subreddit With Most Self Posts', sub_self_post_query.Subreddit.name),
                ('Self Posts', sub_self_post_query.count),
                ('Subreddit With Most Comments', sub_comment_query.Subreddit.name),
                ('Comment Count', sub_comment_query.count),

                ('SEPARATOR', None),
                ('User With Highest Score', user_high_score.User.name),
                ('High Score', user_high_score.score),
                ('User With Lowest Score', user_low_score.User.name),
                ('Low Score', user_low_score.score),
                ('Subreddit With Highest Score', sub_high_score.Subreddit.name),
                ('High Score', sub_high_score.score),
                ('Subreddit With Lowest Score', sub_low_score.Subreddit.name),
                ('Low Score', sub_low_score.score),
            ]

            post_count = session.query(Post.id).count()
            nsfw_post_count = session.query(Post.id).filter(Post.nsfw == True).count()
            self_post_count = session.query(Post.id).filter(Post.is_self == True).count()
            common_title_query = session.query(func.count(Post.id).label('count'), Post.title.label('title'))\
                .group_by(Post.title).order_by(desc('count')).first()
            domain_query = session.query(func.count(Post.id).label('count'), Post.domain.label('domain'))\
                .group_by(Post.domain).order_by(desc('count')).first()

            error_base_query = session.query(func.count(Post.id).label('count'), Post.extraction_error.label('error'))\
                .filter(Post.extraction_error != None)
            error_aggregate = error_base_query.group_by(Post.extraction_error)
            common_error_query = error_aggregate.order_by(desc('count')).first()
            least_common_error_query = error_aggregate.order_by('count').first()

            oldest_extracted_post = session.query(Post).order_by(Post.extraction_date).first()
            newest_extracted_post = session.query(Post).order_by(desc(Post.extraction_date)).first()
            oldest_posted_post = session.query(Post).order_by(Post.date_posted).first()
            newest_posted_post = session.query(Post).order_by(desc(Post.date_posted)).first()

            month_query = session.query(func.count(Post.id).label('count'),
                                        extract('month', Post.date_posted).label('month'))\
                .group_by(extract('month', Post.date_posted))
            top_month_query = month_query.order_by(desc('count')).first()
            bottom_month_query = month_query.order_by('count').first()
            year_query = session.query(func.count(Post.id).label('count'),
                                       extract('year', Post.date_posted).label('year'))\
                .group_by(extract('year', Post.date_posted))
            top_year_query = year_query.order_by(desc('count')).first()
            bottom_year_query = year_query.order_by('count').first()

            content_count_sub = session.query(func.count(Content.id).label('count'))\
                .group_by(Content.post_id).subquery()
            min_content_count = session.query(func.min(content_count_sub.c.count)).first()[0]
            max_content_count = session.query(func.max(content_count_sub.c.count)).first()[0]
            avg_content_count = session.query(func.avg(content_count_sub.c.count)).first()[0]

            self.post_map = [
                ('Total Posts', post_count),
                ('Total Extracted Posts', session.query(Post.id).filter(Post.extracted == True).count()),
                ('Total Failed Posts', session.query(Post.id).filter(Post.extraction_error != None).count()),
                ('Total NSFW Posts', nsfw_post_count),
                ('Total Non-NSFW Posts', session.query(Post.id).filter(Post.nsfw == False).count()),
                ('Percentage of NSFW Posts', round((nsfw_post_count / post_count) * 100, 2)),
                ('Number of Self Posts', self_post_count),
                ('Percentage of Self Posts', round((self_post_count / post_count) * 100, 2)),
                ('Highest Score', session.query(func.max(Post.score)).first()[0]),
                ('Lowest Score', session.query(func.min(Post.score)).first()[0]),
                ('Average Score', round(session.query(func.avg(Post.score)).first()[0])),
                ('Most Common Title', common_title_query.title),
                ('Times Title Used', common_title_query.count),
                ('Total Unique Post Domains', session.query(Post.domain).distinct().count()),
                ('Most Common Domain', domain_query.domain),
                ('Posts From Domain', domain_query.count),

                ('SEPARATOR', None),
                ('Oldest Post by Extraction',
                    f'Title, {oldest_extracted_post.title}\nAuthor, {oldest_extracted_post.author.name}'),
                ('Oldest Extraction Date', oldest_extracted_post.extraction_date),
                ('Newest Post by Extraction',
                    f'Title, {newest_extracted_post.title}\nAuthor, {newest_extracted_post.author.name}'),
                ('Newest Extraction Date', newest_extracted_post.extraction_date),
                ('Oldest Post by Post Date',
                    f'Title, {oldest_posted_post.title}\nAuthor, {oldest_posted_post.author.name}'),
                ('Oldest Post Date', oldest_posted_post.date_posted),
                ('Newest Post by Post Date', 
                    f'Title, {newest_posted_post.title}\nAuthor, {newest_posted_post.author.name}'),
                ('Newest Post Date', newest_posted_post.date_posted),

                ('SEPARATOR', None),
                ('Posts With Errors', error_base_query.first().count),
                ('Percentage of Posts With Errors',
                    f'{round((error_base_query.first().count / post_count) * 100, 2)}%'),
                ('Most Common Error', common_error_query.error),
                ('Times Error Encountered', common_error_query.count),
                ('Least Common Error', least_common_error_query.error),
                ('Times Error Encountered', least_common_error_query.count),

                ('SEPARATOR', None),
                ('Most Common Post Month', calendar.month_name[top_month_query.month]),
                ('Posts That Month', top_month_query.count),
                ('Least Common Post Month', calendar.month_name[bottom_month_query.month]),
                ('Posts That Month', bottom_month_query.count),
                ('Most Common Post Year', str(top_year_query.year)),
                ('Posts That Year', top_year_query.count),
                ('Least Common Year', str(bottom_year_query.year)),
                ('Posts That Year', bottom_year_query.count),

                ('SEPARATOR', None),
                ('Fewest Content From Post', min_content_count),
                ('Most Content From Post', max_content_count),
                ('Average Content Per Post', round(avg_content_count)),
            ]

        self.setup_ui()

    def setup_ui(self):
        self.add_separator('Reddit Objects', False)
        self.add_layout_from_map(self.reddit_object_map)
        self.add_separator('Posts', True, heavy=True)
        self.add_layout_from_map(self.post_map)

    def add_separator(self, header, add_line=True, heavy=False):
        if add_line:
            self.stat_layout.addWidget(self.make_horz_line(heavy))
        label = QLabel(header + ':')
        font = QFont()
        font.setBold(True)
        font.setPointSize(13)
        label.setFont(font)
        self.stat_layout.addWidget(label)

    def make_horz_line(self, heavy=False):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        if heavy:
            line.setLineWidth(3)
        else:
            line.setFrameShadow(QFrame.Sunken)
        return line

    def add_layout_from_map(self, item_map):
        widget = QWidget()
        layout = QFormLayout()
        layout.setContentsMargins(15, 5, 15, 25)
        widget.setLayout(layout)
        row = 0
        for key, value in item_map:
            if key == 'SEPARATOR':
                layout.setWidget(row, QFormLayout.SpanningRole, self.make_horz_line())
            elif key == 'SUB_HEADER':
                label = QLabel(value)
                font = QFont()
                font.setBold(True)
                font.setPointSize(9)
                label.setFont(font)
                layout.setWidget(row, QFormLayout.SpanningRole, label)
            else:
                if type(value) == int:
                    value = self.format_number(value)
                elif type(value) == datetime:
                    value = self.format_datetime(value)
                layout.addRow(QLabel(key + ':'), QLabel(str(value)))
            row += 1
        self.stat_layout.addWidget(widget)

    def format_number(self, number):
        return '{:,}'.format(number)

    def format_datetime(self, date_time):
        return date_time.strftime('%m/%d/%Y %I:%M %p')

    def get_user_content_count_sub(self, session, ext):
        return session.query(Content.user_id, func.count(Content.id).label('count'))\
            .filter(Content.extension.in_(self.get_ext(ext))).group_by(Content.user_id).subquery()

    def get_subreddit_content_count_sub(self, session, ext):
        return session.query(Content.subreddit_id, func.count(Content.id).label('count')) \
            .filter(Content.extension.in_(self.get_ext(ext))).group_by(Content.subreddit_id).subquery()

    def get_user_extension_query(self, session, ext):
        sub = self.get_user_content_count_sub(session, ext)
        return session.query(User, 'count').outerjoin(sub, sub.c.user_id == User.id).order_by(desc('count')).first()

    def get_sub_extension_query(self, session, ext):
        sub = self.get_subreddit_content_count_sub(session, ext)
        return session.query(Subreddit, 'count').outerjoin(sub, sub.c.subreddit_id == Subreddit.id)\
            .order_by(desc('count')).first()

    def get_ext(self, ext_type):
        if ext_type == 'IMG':
            t = Const.IMAGE_EXT
        elif ext_type == 'VID':
            t = Const.VID_EXT
        else:
            t = Const.GIF_EXT
        return (x.replace('.', '') for x in t)

    def closeEvent(self, event):
        self.settings_manager.database_statistics_geom = {
            'width': self.width(),
            'height': self.height(),
            'x': self.x(),
            'y': self.y()
        }
