import os
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QFormLayout, QScrollArea, QWidget, QFrame
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QFont
from sqlalchemy.sql import func
from sqlalchemy import desc, extract
from datetime import datetime
import calendar

from DownloaderForReddit.Database.Models import (DownloadSession, RedditObject, User, Subreddit, Post, Content, Comment,
                                                RedditObjectList)
from DownloaderForReddit.Utils import Injector, SystemUtil
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

        self.stat_count = 0

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

            user_score = session.query(User, func.sum(Post.score).label('score')).join(Post, Post.author_id == User.id)\
                .group_by(User.id)
            significant_user_high_score = user_score.filter(User.significant == True).order_by(desc('score')).first()
            non_sig_user_high_score = user_score.filter(User.significant == False).order_by(desc('score')).first()
            significant_user_low_score = user_score.filter(User.significant == True).order_by('score').first()
            non_sig_user_low_score = user_score.filter(User.significant == False).order_by('score').first()

            sub_score = session.query(Subreddit, func.sum(Post.score).label('score'))\
                .join(Post, Post.subreddit_id == Subreddit.id).group_by(Subreddit.id)
            significant_sub_high_score = sub_score.filter(Subreddit.significant == True)\
                .order_by(desc('score')).first()
            non_sig_sub_high_score = sub_score.filter(Subreddit.significant == False).order_by(desc('score')).first()
            significant_sub_low_score = sub_score.filter(Subreddit.significant == True).order_by('score').first()
            non_sig_sub_low_score = sub_score.filter(Subreddit.significant == False).order_by('score').first()

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
                ('Significant User With Highest Score', significant_user_high_score.User.name),
                ('High Score', significant_user_high_score.score),
                ('Non-Significant User With Highest Score', non_sig_user_high_score.User.name),
                ('High Score', non_sig_user_high_score.score),
                ('Significant User With Lowest Score', significant_user_low_score.User.name),
                ('Low Score', significant_user_low_score.score),
                ('Non-Significant User With Lowest Score', non_sig_user_low_score.User.name),
                ('Low Score', non_sig_user_low_score.score),
                ('Significant Subreddit With Highest Score', significant_sub_high_score.Subreddit.name),
                ('High Score', significant_sub_high_score.score),
                ('Non-Significant Subreddit With Highest Score', non_sig_sub_high_score.Subreddit.name),
                ('High Score', non_sig_sub_high_score.score),
                ('Significant Subreddit With Lowest Score', significant_sub_low_score.Subreddit.name),
                ('Low Score', significant_sub_low_score.score),
                ('Non-Significant Subreddit With Lowest Score', non_sig_sub_low_score.Subreddit.name),
                ('Low Score', non_sig_sub_low_score.score),
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

            post_date_query = session.query(func.count(Post.id).label('count'),
                                            func.DATE(Post.date_posted).label('date'))\
                .group_by(func.DATE(Post.date_posted)).filter(Post.date_posted != None)
            most_posted_date = post_date_query.order_by(desc('count')).first()
            least_posted_date = post_date_query.order_by('count').first()
            month_query = session.query(func.count(Post.id).label('count'),
                                        extract('month', Post.date_posted).label('month'))\
                .group_by(extract('month', Post.date_posted)).filter(Post.date_posted != None)
            top_month_query = month_query.order_by(desc('count')).first()
            bottom_month_query = month_query.order_by('count').first()
            dow_query = session.query(func.count(Post.id).label('count'),
                                      extract('dow', Post.date_posted).label('dow')) \
                .group_by(extract('dow', Post.date_posted)).filter(Post.date_posted != None)
            top_dow_query = dow_query.order_by(desc('count')).first()
            bottom_dow_query = dow_query.order_by('count').first()
            year_query = session.query(func.count(Post.id).label('count'),
                                       extract('year', Post.date_posted).label('year'))\
                .group_by(extract('year', Post.date_posted)).filter(Post.date_posted != None)
            top_year_query = year_query.order_by(desc('count')).first()
            bottom_year_query = year_query.order_by('count').first()

            extraction_date_query = session.query(func.count(Post.id).label('count'),
                                                  func.DATE(Post.extraction_date).label('date'))\
                .group_by(func.DATE(Post.extraction_date)).filter(Post.extraction_date != None)
            most_extracted_date = extraction_date_query.order_by(desc('count')).first()
            least_extracted_date = extraction_date_query.order_by('count').first()
            extraction_month_query = session.query(func.count(Post.id).label('count'),
                                                   extract('month', Post.extraction_date).label('month'))\
                .group_by(extract('month', Post.extraction_date)).filter(Post.extraction_date != None)
            most_extracted_month = extraction_month_query.order_by(desc('count')).first()
            least_extracted_month = extraction_month_query.order_by('count').first()
            dow_extraction = session.query(func.count(Post.id).label('count'),
                                           extract('dow', Post.extraction_date).label('dow'))\
                .group_by(extract('dow', Post.extraction_date)).filter(Post.extraction_date != None)
            top_dow_extraction = dow_extraction.order_by(desc('count')).first()
            bottom_dow_extraction = dow_extraction.order_by('count').first()

            content_count_sub = session.query(func.count(Content.id).label('count'))\
                .group_by(Content.post_id).subquery()
            min_content_count = session.query(func.min(content_count_sub.c.count)).first()[0]
            max_content_count = session.query(func.max(content_count_sub.c.count)).first()[0]
            avg_content_count = session.query(func.avg(content_count_sub.c.count)).first()[0]

            self.post_map = [
                ('Total Posts', post_count),
                ('Total Extracted Posts', session.query(Post.id).filter(Post.extracted == True).count()),
                ('Total NSFW Posts', nsfw_post_count),
                ('Total Non-NSFW Posts', session.query(Post.id).filter(Post.nsfw == False).count()),
                ('Percentage of NSFW Posts', self.get_percentage(nsfw_post_count, post_count)),
                ('Number of Self Posts', self_post_count),
                ('Percentage of Self Posts', self.get_percentage(self_post_count, post_count)),
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
                    f'Title: {oldest_extracted_post.title}\nAuthor: {oldest_extracted_post.author.name}'),
                ('Oldest Extraction Date', oldest_extracted_post.extraction_date),
                ('Newest Post by Extraction',
                    f'Title: {newest_extracted_post.title}\nAuthor: {newest_extracted_post.author.name}'),
                ('Newest Extraction Date', newest_extracted_post.extraction_date),
                ('Oldest Post by Post Date',
                    f'Title: {oldest_posted_post.title}\nAuthor: {oldest_posted_post.author.name}'),
                ('Oldest Post Date', oldest_posted_post.date_posted),
                ('Newest Post by Post Date', 
                    f'Title: {newest_posted_post.title}\nAuthor: {newest_posted_post.author.name}'),
                ('Newest Post Date', newest_posted_post.date_posted),

                ('SEPARATOR', None),
                ('Posts With Errors', error_base_query.first().count),
                ('Percentage of Posts With Errors', self.get_percentage(error_base_query.first().count, post_count)),
                ('Most Common Error', common_error_query.error),
                ('Times Error Encountered', common_error_query.count),
                ('Least Common Error', least_common_error_query.error),
                ('Times Error Encountered', least_common_error_query.count),

                ('SEPARATOR', None),
                ('SUB_HEADER', 'Post Dates:'),
                ('Most Posted Date', self.format_date_string(most_posted_date.date)),
                ('Posts That Day',
                    f'{most_posted_date.count}  ({self.get_percentage(most_posted_date.count, post_count)})'),
                ('Least Posted Day', self.format_date_string(least_posted_date.date)),
                ('Posts That Day',
                    f'{least_posted_date.count}  ({self.get_percentage(least_posted_date.count, post_count)})'),
                ('Most Common Post Month', calendar.month_name[top_month_query.month]),
                ('Posts That Month',
                    f'{top_month_query.count}  ({self.get_percentage(top_month_query.count, post_count)})'),
                ('Least Common Post Month', calendar.month_name[bottom_month_query.month]),
                ('Posts That Month',
                    f'{bottom_month_query.count}  ({self.get_percentage(bottom_month_query.count, post_count)})'),
                ('Most Popular Day of The Week', calendar.day_name[top_dow_query.dow]),
                ('Posts That Day',
                    f'{top_dow_query.count}  ({self.get_percentage(top_dow_query.count, post_count)})'),
                ('Least Popular Day of The Week', calendar.day_name[bottom_dow_query.dow]),
                ('Posts That Day',
                    f'{bottom_dow_query.count}  ({self.get_percentage(bottom_dow_query.count, post_count)})'),
                ('Most Common Post Year', str(top_year_query.year)),
                ('Posts That Year',
                    f'{top_year_query.count}  ({self.get_percentage(top_year_query.count, post_count)})'),
                ('Least Common Year', str(bottom_year_query.year)),
                ('Posts That Year',
                    f'{bottom_year_query.count}  ({self.get_percentage(bottom_year_query.count, post_count)})'),

                ('SEPARATOR', None),
                ('SUB_HEADER', 'Extraction Dates:'),
                ('Most Extracted Date', self.format_date_string(most_extracted_date.date)),
                ('Extracted That Day',
                    f'{most_extracted_date.count}  ({self.get_percentage(most_extracted_date.count, post_count)})'),
                ('Least Extracted Date', self.format_date_string(least_extracted_date.date)),
                ('Extracted That Day',
                    f'{least_extracted_date.count}  ({self.get_percentage(least_extracted_date.count, post_count)}'),
                ('Most Extracted Month', calendar.month_name[most_extracted_month.month]),
                ('Extractions That Month',
                    f'{most_extracted_month.count}  ({self.get_percentage(most_extracted_month.count, post_count)})'),
                ('Least Extracted Month', calendar.month_name[least_extracted_month.month]),
                ('Extractions That Month',
                    f'{least_extracted_month.count}  ({self.get_percentage(least_extracted_month.count, post_count)})'),
                ('Most Extracted Day of The Week', calendar.day_name[top_dow_extraction.dow]),
                ('Posts That Day',
                    f'{top_dow_extraction.count}  ({self.get_percentage(top_dow_extraction.count, post_count)})'),
                ('Least Extracted Day of The Week', calendar.day_name[bottom_dow_extraction.dow]),
                ('Posts That Day',
                    f'{bottom_dow_extraction.count}  ({self.get_percentage(bottom_dow_extraction.count, post_count)})'),

                ('SEPARATOR', None),
                ('Fewest Content From Post', min_content_count),
                ('Most Content From Post', max_content_count),
                ('Average Content Per Post', round(avg_content_count)),
            ]

            content_count = session.query(Content.id).count()
            downloaded_content_count = session.query(Content.id).filter(Content.downloaded == True).count()

            content_exts = session.query(func.count(Content.id).label('count'), Content.extension.label('ext'))\
                .group_by(Content.extension).filter(Content.extension != None)
            most_used_extension = content_exts.order_by(desc('count')).first()
            least_used_extension = content_exts.order_by('count').first()

            content_from_posts = session.query(Content.id).filter(Content.comment_id == None).count()

            download_error_count = session.query(Content.id).filter(Content.download_error != None).count()
            content_error_base = session.query(func.count(Content.id).label('count'),
                                               Content.download_error.label('error'))\
                .filter(Content.download_error != None)
            content_error_aggregate = content_error_base.group_by(Content.download_error)
            common_download_error_query = content_error_aggregate.order_by(desc('count')).first()
            least_common_download_error_query = content_error_aggregate.order_by('count').first()

            content_date_query = session.query(func.count(Content.id).label('count'),
                                               func.DATE(Content.download_date).label('date'))\
                .group_by(func.DATE(Content.download_date)).filter(Content.download_date != None)
            most_downloaded_date = content_date_query.order_by(desc('count')).first()
            least_downloaded_date = content_date_query.order_by('count').first()
            content_month_query = session.query(func.count(Content.id).label('count'),
                                                extract('month', Content.download_date).label('month'))\
                .group_by(extract('month', Content.download_date)).filter(Content.download_date != None)
            content_top_month_query = content_month_query.order_by(desc('count')).first()
            content_bottom_month_query = content_month_query.order_by('count').first()
            content_dow_query = session.query(func.count(Content.id).label('count'),
                                              extract('dow', Content.download_date).label('dow'))\
                .group_by(extract('dow', Content.download_date)).filter(Content.download_date != None)
            content_top_dow_query = content_dow_query.order_by(desc('count')).first()
            content_bottom_dow_query = content_dow_query.order_by('count').first()
            content_year_query = session.query(func.count(Content.id).label('count'),
                                               extract('year', Content.download_date).label('year'))\
                .group_by(extract('year', Content.download_date)).filter(Content.download_date != None)
            content_top_year = content_year_query.order_by(desc('count')).first()
            content_bottom_year = content_year_query.order_by('count').first()

            self.content_map = [
                ('Total Content', content_count),
                ('Downloaded Content', downloaded_content_count),
                ('Percentage Downloaded', f'{self.get_percentage(downloaded_content_count, content_count)}%'),
                ('Content Not Downloaded\n(non-error)', content_count - downloaded_content_count),
                ('Percentage Not Downloaded\n(non-error)',
                    f'{self.get_percentage((content_count - downloaded_content_count), content_count)}%'),
                ('SEPARATOR', None),
                ('Most Common Extension', most_used_extension.ext),
                ('Extension Used',
                     f'{most_used_extension.count}  ({self.get_percentage(most_used_extension.count, content_count)})'),
                ('Least Common Extension', least_used_extension.ext),
                ('Extension Used',
                    f'{least_used_extension.count}  '
                    f'({self.get_percentage(least_used_extension.count, content_count)})'),

                ('SEPARATOR', None),
                ('Content From Posts', content_from_posts),
                ('Percent From Posts', f'{self.get_percentage(content_from_posts, content_count)}%'),
                ('Content From Comments', content_count - content_from_posts),
                ('Percent From Comments',
                    f'{self.get_percentage((content_count - content_from_posts), content_count)}%'),

                ('SEPARATOR', None),
                ('Download Errors', download_error_count),
                ('Most Common Error', common_download_error_query.error),
                ('Times Encountered', common_download_error_query.count),
                ('Least Common Error', least_common_download_error_query.error),
                ('Times Encountered', least_common_download_error_query.count),

                ('SEPARATOR', None),
                ('SUB_HEADER', 'Download Dates:'),
                ('Most Downloaded Date', self.format_date_string(most_downloaded_date.date)),
                ('Downloaded on This Date',
                    f'{most_downloaded_date.count}  '
                    f'({self.get_percentage(most_downloaded_date.count, content_count)})'),
                ('Least Downloaded Date', self.format_date_string(least_downloaded_date.date)),
                ('Downloaded on This Date',
                    f'{least_downloaded_date.count}  '
                    f'({self.get_percentage(least_downloaded_date.count, content_count)})'),
                ('Most Common Download Month', calendar.month_name[content_top_month_query.month]),
                ('Downloads That Month',
                    f'{content_top_month_query.count}  '
                    f'({self.get_percentage(content_top_month_query.count, content_count)})'),
                ('Least Common Download Month', calendar.month_name[content_bottom_month_query.month]),
                ('Downloads That Month',
                    f'{content_bottom_month_query.count}  '
                    f'({self.get_percentage(content_bottom_month_query.count, content_count)})'),
                ('Most Popular Day of The Week', calendar.day_name[content_top_dow_query.dow]),
                ('Downloads That Day', f'{content_top_dow_query.count}  '
                                       f'({self.get_percentage(content_top_dow_query.count, content_count)})'),
                ('Least Popular Day of The Week', calendar.day_name[content_bottom_dow_query.dow]),
                ('Downloads That Day',
                    f'{content_bottom_dow_query.count}  '
                    f'({self.get_percentage(content_bottom_dow_query.count, content_count)})'),
                ('Most Common Download Year', str(content_top_year.year)),
                ('Downloads That Year', f'{content_top_year.count}  '
                                        f'({self.get_percentage(content_top_year.count, content_count)})'),
                ('Least Common Download Year', str(content_bottom_year.count)),
                ('Downloads That Year', f'{content_bottom_year.count}  '
                                        f'({self.get_percentage(content_bottom_year.count, content_count)})')
            ]

            session_count = session.query(DownloadSession.id).count()
            completed_sessions = session.query(DownloadSession.id).filter(DownloadSession.end_time != None).count()
            incomplete_sessions = session_count - completed_sessions
            oldest_session = session.query(DownloadSession).order_by(DownloadSession.start_time).first()
            newest_session = session.query(DownloadSession).order_by(desc(DownloadSession.start_time)).first()
            session_post_extraction = session.query(func.count(Post.download_session_id).label('count'))\
                .group_by(Post.download_session_id)
            most_extracted = session_post_extraction.order_by(desc('count')).first()
            least_extracted = session_post_extraction.order_by('count').first()
            session_content_download = session.query(func.count(Content.download_session_id).label('count'))\
                .group_by(Content.download_session_id)
            most_downloaded = session_content_download.order_by(desc('count')).first()
            least_downloaded = session_content_download.order_by('count').first()

            shortest_download_session = session.query(DownloadSession).filter(DownloadSession.duration != None)\
                .filter(DownloadSession.duration >= 0).order_by(DownloadSession.duration).first()
            longest_download_session = session.query(DownloadSession).filter(DownloadSession.duration != None)\
                .filter(DownloadSession.duration >= 0).order_by(desc(DownloadSession.duration)).first()

            run_date_query = session.query(func.count(DownloadSession.id).label('count'),
                                             func.DATE(DownloadSession.start_time).label('date'))\
                .group_by(func.DATE(DownloadSession.start_time)).filter(DownloadSession.start_time != None)
            most_run_date = run_date_query.order_by(desc('count')).first()
            least_run_date = run_date_query.order_by('count').first()
            run_month_query = session.query(func.count(DownloadSession.id).label('count'),
                                            extract('month', DownloadSession.start_time).label('month'))\
                .group_by(extract('month', DownloadSession.start_time)).filter(DownloadSession.start_time != None)
            most_run_month = run_month_query.order_by(desc('count')).first()
            least_run_month = run_month_query.order_by('count').first()
            run_dow_query = session.query(func.count(DownloadSession.id).label('count'),
                                            extract('dow', DownloadSession.start_time).label('dow'))\
                .group_by(extract('dow', DownloadSession.start_time)).filter(DownloadSession.start_time != None)
            top_run_dow = run_dow_query.order_by(desc('count')).first()
            bottom_run_dow = run_dow_query.order_by('count').first()

            self.download_sessions_map = [
                ('Total Download Sessions', session_count),
                ('Completed Sessions',
                    f'{completed_sessions}  ({self.get_percentage(completed_sessions, session_count)})'),
                ('Incomplete Sessions',
                    f'{incomplete_sessions}  ({self.get_percentage(incomplete_sessions, session_count)})'),
                ('Oldest Session', oldest_session.name),
                ('Run Date', oldest_session.start_time),
                ('Newest Session', newest_session.name),
                ('Run Date', newest_session.start_time),
                ('Most Extracted Posts', most_extracted),
                ('Least Extracted Posts', least_extracted),
                ('Most Downloaded Content', most_downloaded),
                ('Least Downloaded Content', least_downloaded),

                ('SEPARATOR', None),
                ('Average Download Time',
                    SystemUtil.get_duration_str(session.query(func.avg(DownloadSession.duration))
                                                .filter(DownloadSession.duration >= 0).first()[0])),
                ('Shortest Download Session', shortest_download_session.name),
                ('Shorted Download Time', SystemUtil.get_duration_str(shortest_download_session.duration)),
                ('Posts Extracted', session.query(Post.id)
                    .filter(Post.download_session_id == shortest_download_session.id)
                    .filter(Post.extracted == True).count()),
                ('Content Downloaded', session.query(Content.id)
                    .filter(Content.download_session_id == shortest_download_session.id)
                    .filter(Content.downloaded == True).count()),
                ('Longest Download Session', longest_download_session.name),
                ('Longest Download Time', SystemUtil.get_duration_str(longest_download_session.duration)),
                ('Posts Extracted', session.query(Post.id)
                    .filter(Post.download_session_id == longest_download_session.id)
                    .filter(Post.extracted == True).count()),
                ('Content Downloaded', session.query(Content.id)
                    .filter(Content.download_session_id == longest_download_session.id)
                    .filter(Content.downloaded == True).count()),

                ('SEPARATOR', None),
                ('Most Run Date', self.format_date_string(most_run_date.date)),
                ('Runs On This Date',
                    f'{most_run_date.count}  ({self.get_percentage(most_run_date.count, session_count)})'),
                ('Least Run Date', self.format_date_string(least_run_date.date)),
                ('Runs On This Date',
                    f'{least_run_date.count}  ({self.get_percentage(least_run_date.count, session_count)})'),
                ('Most Run Month', calendar.month_name[most_run_month.month]),
                ('Runs That Month',
                    f'{most_run_month.count}  ({self.get_percentage(most_run_month.count, session_count)})'),
                ('Least Run Month', calendar.month_name[least_run_month.month]),
                ('Runs That Month',
                    f'{least_run_month.count}  ({self.get_percentage(least_run_month.count, session_count)})'),
                ('Most Run Day of The Week', calendar.day_name[top_run_dow.dow]),
                ('Runs This Day',
                    f'{top_run_dow.count}  ({self.get_percentage(top_run_dow.count, session_count)})'),
                ('Least Run Day of The Week', calendar.day_name[bottom_run_dow.dow]),
                ('Runs This Day',
                    f'{bottom_run_dow.count}  ({self.get_percentage(bottom_run_dow.count, session_count)})')
            ]

            self.database_map = [
                ('Total Items In Database', self.get_total_row_count(session)),
                ('Database File Size', SystemUtil.format_size(os.path.getsize(self.db.database_path))),
                
            ]

        self.setup_ui()

    def get_percentage(self, x, y):
        """
        Returns the percentage X is of Y as a string.
        :param x: The smaller number which is some percentage of Y.
        :param y: The larger number of which X represents some percentage of.
        :return: X percent of Y as a string.
        """
        return f'{round((x / y) * 100, 2)}%'

    def setup_ui(self):
        self.add_separator('Reddit Objects', False)
        self.add_layout_from_map(self.reddit_object_map)
        self.add_separator('Posts', True, heavy=True)
        self.add_layout_from_map(self.post_map)
        self.add_separator('Content', True, heavy=True)
        self.add_layout_from_map(self.content_map)
        self.add_separator('Download Sessions', True, heavy=True)
        self.add_layout_from_map(self.download_sessions_map)
        self.add_separator('Database', True, heavy=True)
        self.add_layout_from_map(self.database_map)

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
                value_type = type(value)
                if value_type == int:
                    value = self.format_number(value)
                elif value_type == datetime:
                    value = self.format_datetime(value)
                layout.addRow(QLabel(key + ':'), QLabel(str(value)))
                self.stat_count += 1
            row += 1
        self.stat_layout.addWidget(widget)

    def format_number(self, number):
        return '{:,}'.format(number)

    def format_datetime(self, date_time):
        return date_time.strftime('%m/%d/%Y %I:%M %p')

    def format_date_string(self, date_string):
        return datetime.strptime(date_string, '%Y-%m-%d').date().strftime('%m/%d/%Y')

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

    def get_total_row_count(self, session):
        count = 0
        for model in [RedditObject, DownloadSession, RedditObjectList, Post, Content, Comment]:
            count += session.query(model.id).count()
        return count

    def closeEvent(self, event):
        self.settings_manager.database_statistics_geom = {
            'width': self.width(),
            'height': self.height(),
            'x': self.x(),
            'y': self.y()
        }
