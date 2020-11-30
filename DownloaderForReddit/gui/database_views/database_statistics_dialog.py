import os
import logging
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QFormLayout, QScrollArea, QWidget, QFrame
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QFont, QIcon, QPixmap
from sqlalchemy.sql import func
from sqlalchemy import desc, extract
from datetime import datetime
import calendar
from time import time
from operator import attrgetter

from DownloaderForReddit.database.models import (DownloadSession, RedditObject, User, Subreddit, Post, Content, Comment,
                                                 RedditObjectList, ListAssociation)
from DownloaderForReddit.utils import injector, system_util, general_utils
from DownloaderForReddit.core import const


class DatabaseStatisticsDialog(QDialog):

    def __init__(self):
        QDialog.__init__(self)
        self.logger = logging.getLogger(f'DownloaderForReddit.{__name__}')
        self.db = injector.get_database_handler()
        self.settings_manager = injector.get_settings_manager()

        self.setWindowTitle('Database Statistics')
        icon = QIcon()
        icon.addPixmap(QPixmap('Resources/images/statistics_icon.png'), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)

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
        start_time = time()

        try:
            with self.db.get_scoped_session() as session:
                total_reddit_objects = session.query(RedditObject.id).count()
                total_significant = session.query(RedditObject.id).filter(RedditObject.significant == True).count()

                self.reddit_object_map = [
                    ('Total Users/Subreddits', total_reddit_objects),
                    ('Total Significant Users/Subreddits', total_significant,
                        '"Significant" indicates users/subreddits that you have added to a list yourself'),
                    ('Total Non-Significant Users/Subreddits', total_reddit_objects - total_significant,
                        'Non-Significant users/subreddits are ones that have been added by the application'),
                ]

                post_count = session.query(Post.id).count()
                total_score = session.query(func.sum(Post.score)).scalar()

                total_users = session.query(User.id).count()
                total_significant_users = session.query(User.id).filter(User.significant == True).count()

                oldest_user = session.query(User).order_by(User.date_added).first()
                newest_user = session.query(User).order_by(desc(User.date_added)).first()

                user_count_sub = session.query(Post.significant_reddit_object_id, func.count(Post.id).label('count')) \
                    .group_by(Post.significant_reddit_object_id).subquery()
                user_count = session.query(User, 'count') \
                    .outerjoin(user_count_sub, user_count_sub.c.significant_reddit_object_id == User.id) \
                    .order_by(desc('count')).first()

                user_score = session.query(User, func.sum(Post.score).label('score'))\
                    .join(Post, Post.author_id == User.id).group_by(User.id)
                significant_user_high_score = user_score.filter(User.significant == True).order_by(desc('score')).first()
                non_sig_user_high_score = user_score.filter(User.significant == False).order_by(desc('score')).first()
                significant_user_low_score = user_score.filter(User.significant == True).order_by('score').first()
                non_sig_user_low_score = user_score.filter(User.significant == False).order_by('score').first()

                user_image_query = self.get_user_extension_query(session, 'IMG')
                user_video_query = self.get_user_extension_query(session, 'VID')
                user_gif_query = self.get_user_extension_query(session, 'GIF')

                self_post_sub = session.query(Post.significant_reddit_object_id, func.count(Post.id).label('count')) \
                    .filter(Post.is_self == True).group_by(Post.significant_reddit_object_id).subquery()
                user_self_post_query = session.query(User, 'count') \
                    .outerjoin(self_post_sub, self_post_sub.c.significant_reddit_object_id == User.id) \
                    .order_by(desc('count')).first()

                comment_author_sub = session.query(Comment.author_id, func.count(Comment.id).label('count')) \
                    .group_by(Comment.author_id).subquery()
                user_comment_query = session.query(User, 'count') \
                    .outerjoin(comment_author_sub, comment_author_sub.c.author_id == User.id) \
                    .order_by(desc('count')).first()

                self.user_map = [
                    ('Total Users',
                        f'{self.format_number(total_users)}  '
                        f'({self.get_percentage(total_users, total_reddit_objects)} of reddit objects)'),
                    ('Total Significant Users',
                        f'{self.format_number(total_significant_users)}  '
                        f'({self.get_percentage(total_significant_users, total_users)} of users)'),
                    ('Total Non-Significant Users',
                        f'{self.format_number(total_users - total_significant_users)}  '
                        f'{self.get_percentage(total_users - total_significant, total_users)} of users)'),

                    ('SEPARATOR', None),
                    ('Oldest User', self.get(oldest_user, 'name')),
                    ('User Added', self.get(oldest_user, 'date_added')),
                    ('Newest User', self.get(newest_user, 'name')),
                    ('User Added', self.get(newest_user, 'date_added')),

                    ('SEPARATOR', None),
                    ('User With Most Posts', self.get(user_count, 'User.name')),
                    ('Post Count',
                        f'{self.format_number(user_count.count)}  '
                        f'({self.get_percentage(user_count.count, post_count)} of all posts)'),

                    ('SEPARATOR', None),
                    ('User With Most Images', self.get(user_image_query, 'User.name')),
                    ('Image Count', self.get(user_image_query, 'count')),
                    ('User With Most Videos', self.get(user_video_query, 'User.name')),
                    ('Video Count', self.get(user_video_query, 'count')),
                    ('User With Most Gifs', self.get(user_gif_query, 'User.name')),
                    ('Gif Count', self.get(user_gif_query, 'count')),
                    ('User With Most Self Posts', self.get(user_self_post_query, 'User.name')),
                    ('Self Posts', self.get(user_self_post_query, 'count')),
                    ('User With Most Comments', self.get(user_comment_query, 'User.name')),
                    ('Comment Count', self.get(user_comment_query, 'count')),

                    ('SEPARATOR', None),
                    ('Significant User With Highest Score', self.get(significant_user_high_score, 'User.name')),
                    ('High Score', self.get(significant_user_high_score, 'score')),
                    ('Non-Significant User With Highest Score', self.get(non_sig_user_high_score, 'User.name')),
                    ('High Score', self.get(non_sig_user_high_score, 'score')),
                    ('Significant User With Lowest Score', self.get(significant_user_low_score, 'User.name')),
                    ('Low Score', self.get(significant_user_low_score, 'score')),
                    ('Non-Significant User With Lowest Score', self.get(non_sig_user_low_score, 'User.name')),
                    ('Low Score', self.get(non_sig_user_low_score, 'score')),
                ]

                total_subreddits = session.query(Subreddit.id).count()
                total_significant_subreddits = session.query(Subreddit.id).filter(Subreddit.significant == True).count()
                non_significant_subreddits = total_subreddits - total_significant_subreddits

                oldest_sub = session.query(Subreddit).order_by(Subreddit.date_added).first()
                newest_sub = session.query(Subreddit).order_by(desc(Subreddit.date_added)).first()

                sub_count_sub = session.query(Post.significant_reddit_object_id, func.count(Post.id).label('count')) \
                    .group_by(Post.significant_reddit_object_id).subquery()
                sub_count = session.query(Subreddit, 'count') \
                    .outerjoin(sub_count_sub, sub_count_sub.c.significant_reddit_object_id == Subreddit.id) \
                    .order_by(desc('count')).first()

                subreddit_image_query = self.get_sub_extension_query(session, 'IMG')
                subreddit_video_query = self.get_sub_extension_query(session, 'VID')
                subreddit_gif_query = self.get_sub_extension_query(session, 'GIF')

                sub_self_post_query = session.query(Subreddit, 'count') \
                    .outerjoin(self_post_sub, self_post_sub.c.significant_reddit_object_id == Subreddit.id) \
                    .order_by(desc('count')).first()

                comment_subreddit_sub = session.query(Comment.subreddit_id, func.count(Comment.id).label('count')) \
                    .group_by(Comment.subreddit_id).subquery()
                sub_comment_query = session.query(Subreddit, 'count') \
                    .outerjoin(comment_subreddit_sub, comment_subreddit_sub.c.subreddit_id == Subreddit.id) \
                    .order_by(desc('count')).first()

                sub_score = session.query(Subreddit, func.sum(Post.score).label('score')) \
                    .join(Post, Post.subreddit_id == Subreddit.id).group_by(Subreddit.id)
                significant_sub_high_score = sub_score.filter(Subreddit.significant == True) \
                    .order_by(desc('score')).first()
                non_sig_sub_high_score = sub_score.filter(Subreddit.significant == False).order_by(desc('score')).first()
                significant_sub_low_score = sub_score.filter(Subreddit.significant == True).order_by('score').first()
                non_sig_sub_low_score = sub_score.filter(Subreddit.significant == False).order_by('score').first()

                self.subreddit_map = [
                    ('Total Subreddits',
                        f'{self.format_number(total_subreddits)}  '
                        f'({self.get_percentage(total_subreddits, total_reddit_objects)} of reddit objects)'),
                    ('Total Significant Subreddits',
                        f'{self.format_number(total_significant_subreddits)}  '
                        f'({self.get_percentage(total_significant_subreddits, total_subreddits)} of subreddits)'),
                    ('Total Non-Significant Subreddits',
                        f'{self.format_number(non_significant_subreddits)}  '
                        f'({self.get_percentage(non_significant_subreddits, total_subreddits)} of subreddits)'),

                    ('SEPARATOR', None),
                    ('Oldest Subreddit', self.get(oldest_sub, 'name')),
                    ('Subreddit Added', self.get(oldest_sub, 'date_added')),
                    ('Newest Subreddit', self.get(newest_sub, 'name')),
                    ('Subreddit Added', self.get(newest_sub, 'date_added')),

                    ('SEPARATOR', None),
                    ('Subreddit With Most Posts', self.get(sub_count, 'Subreddit.name')),
                    ('Post Count',
                        f'{self.format_number(self.get(sub_count, "count"))}  '
                        f'({self.get_percentage(self.get(sub_count, "count"), post_count)} of all posts)'),

                    ('SEPARATOR', None),
                    ('Subreddit With Most Images', self.get(subreddit_image_query, 'Subreddit.name')),
                    ('Image Count', self.get(subreddit_image_query, 'count')),
                    ('Subreddit With Most Videos', self.get(subreddit_video_query, 'Subreddit.name')),
                    ('Video Count', self.get(subreddit_video_query, 'count')),
                    ('Subreddit With Most Gifs', self.get(subreddit_gif_query, 'Subreddit.name')),
                    ('Gif Count', self.get(subreddit_gif_query, 'count')),
                    ('Subreddit With Most Self Posts', self.get(sub_self_post_query, 'Subreddit.name')),
                    ('Self Posts', self.get(sub_self_post_query, 'count')),
                    ('Subreddit With Most Comments', self.get(sub_comment_query, 'Subreddit.name')),
                    ('Comment Count', self.get(sub_comment_query, 'count')),

                    ('SEPARATOR', None),
                    ('Significant Subreddit With Highest Score', self.get(significant_sub_high_score, 'Subreddit.name')),
                    ('High Score', self.get(significant_sub_high_score, 'score')),
                    ('Non-Significant Subreddit With Highest Score', self.get(non_sig_sub_high_score, 'Subreddit.name')),
                    ('High Score', self.get(non_sig_sub_high_score, 'score')),
                    ('Significant Subreddit With Lowest Score', self.get(significant_sub_low_score, 'Subreddit.name')),
                    ('Low Score', self.get(significant_sub_low_score, 'score')),
                    ('Non-Significant Subreddit With Lowest Score', self.get(non_sig_sub_low_score, 'Subreddit.name')),
                    ('Low Score', self.get(non_sig_sub_low_score, 'score')),
                ]

                total_lists = session.query(RedditObjectList.id).count()
                user_lists = session.query(RedditObjectList.id).filter(RedditObjectList.list_type == 'USER').count()
                sub_lists = session.query(RedditObjectList.id).filter(RedditObjectList.list_type == 'SUBREDDIT').count()
                oldest_list = session.query(RedditObjectList).order_by(RedditObjectList.date_created).first()
                newest_list = session.query(RedditObjectList).order_by(desc(RedditObjectList.date_created)).first()

                list_item_count_query = session.query(func.count(ListAssociation.reddit_object_id).label('count'),
                                                      RedditObjectList).join(RedditObjectList) \
                    .group_by(ListAssociation.reddit_object_list_id)
                avg_items_in_list = session.query(func.avg(list_item_count_query.subquery().c.count)).scalar()
                list_with_most_items = list_item_count_query.order_by(desc('count')).first()
                list_with_fewest_items = list_item_count_query.order_by('count').first()

                list_post_count_sub = session.query(ListAssociation.reddit_object_list_id,
                                                    Post.significant_reddit_object_id,
                                                    func.count(Post.id).label('count'))\
                    .join(Post, Post.significant_reddit_object_id == ListAssociation.reddit_object_id)\
                    .group_by(ListAssociation.reddit_object_list_id).subquery()
                list_post_base = session.query(RedditObjectList, 'count')\
                    .outerjoin(list_post_count_sub, RedditObjectList.id == list_post_count_sub.c.reddit_object_list_id)
                list_with_most_posts = list_post_base.order_by(desc('count')).first()
                list_with_fewest_posts = list_post_base.order_by('count').first()

                list_score_sub = session.query(ListAssociation.reddit_object_list_id,
                                               Post.significant_reddit_object_id,
                                               func.sum(Post.score).label('score')) \
                    .join(Post, Post.significant_reddit_object_id == ListAssociation.reddit_object_id) \
                    .group_by(ListAssociation.reddit_object_list_id).subquery()
                list_score_base = session.query(RedditObjectList, 'score')\
                    .outerjoin(list_score_sub, RedditObjectList.id == list_score_sub.c.reddit_object_list_id)
                list_with_highest_score = list_score_base.order_by(desc('score')).first()
                list_with_lowest_score = list_score_base.order_by('score').first()

                self.list_map = [
                    ('Total Number of Lists', total_lists),
                    ('Total User Lists', user_lists),
                    ('Total Subreddit Lists', sub_lists),
                    ('Oldest List', self.get(oldest_list, 'name')),
                    ('List Created', self.get(oldest_list, 'date_created')),
                    ('Newest List', self.get(newest_list, 'name')),
                    ('List Created', self.get(newest_list, 'date_created')),

                    ('SEPARATOR', None),
                    ('Average Items Per List', round(avg_items_in_list, 2)),
                    ('List With Most Items', self.get(list_with_most_items, 'RedditObjectList.display_name')),
                    ('Items In List', self.get(list_with_most_items, 'count')),
                    ('List With Fewest Items', self.get(list_with_fewest_items, 'RedditObjectList.display_name')),
                    ('Items In List', self.get(list_with_fewest_items, 'count')),
                    ('List With Most Posts', self.get(list_with_most_posts, 'RedditObjectList.display_name')),
                    ('Posts In List',
                        f'{self.format_number(self.get(list_with_most_posts, "count"))}  '
                        f'({self.get_percentage(self.get(list_with_most_posts, "count"), post_count)} of all posts)'),
                    ('List With Fewest Posts', self.get(list_with_fewest_posts, 'RedditObjectList.display_name')),
                    ('Posts In List',
                        f'{self.format_number(self.get(list_with_fewest_posts, "count"))}  '
                        f'({self.get_percentage(self.get(list_with_most_posts, "count"), post_count)} of all posts)'),
                    ('List With Highest Score', self.get(list_with_highest_score, 'RedditObjectList.display_name')),
                    ('Total Score',
                        f'{self.format_number(self.get(list_with_highest_score, "score"))}  '
                        f'({self.get_percentage(self.get(list_with_highest_score, "score"), total_score)} of total score)'),
                    ('List With Lowest Score', self.get(list_with_lowest_score, 'RedditObjectList.display_name')),
                    ('Total Score',
                        f'{self.format_number(self.get(list_with_lowest_score, "score"))}  '
                        f'({self.get_percentage(self.get(list_with_lowest_score, "score"), total_score)} of total score)')
                ]

                nsfw_post_count = session.query(Post.id).filter(Post.nsfw == True).count()
                non_nsfw_post_count = session.query(Post.id).filter(Post.nsfw == False).count()
                self_post_count = session.query(Post.id).filter(Post.is_self == True).count()
                common_title_query = session.query(func.count(Post.id).label('count'), Post.title.label('title')) \
                    .group_by(Post.title).order_by(desc('count')).first()
                total_domains = session.query(Post.domain).distinct().count()
                domain_query = session.query(func.count(Post.id).label('count'), Post.domain.label('domain')) \
                    .group_by(Post.domain).order_by(desc('count')).first()

                error_base_query = session.query(func.count(Post.id).label('count'), Post.extraction_error.label('error')) \
                    .filter(Post.extraction_error != None)
                error_count = error_base_query.first().count
                error_aggregate = error_base_query.group_by(Post.extraction_error)
                common_error_query = error_aggregate.order_by(desc('count')).first()
                least_common_error_query = error_aggregate.order_by('count').first()

                oldest_extracted_post = session.query(Post).order_by(Post.extraction_date).first()
                newest_extracted_post = session.query(Post).order_by(desc(Post.extraction_date)).first()
                oldest_posted_post = session.query(Post).order_by(Post.date_posted).first()
                newest_posted_post = session.query(Post).order_by(desc(Post.date_posted)).first()

                post_date_query = session.query(func.count(Post.id).label('count'),
                                                func.DATE(Post.date_posted).label('date')) \
                    .group_by(func.DATE(Post.date_posted)).filter(Post.date_posted != None)
                most_posted_date = post_date_query.order_by(desc('count')).first()
                least_posted_date = post_date_query.order_by('count').first()
                month_query = session.query(func.count(Post.id).label('count'),
                                            extract('month', Post.date_posted).label('month')) \
                    .group_by(extract('month', Post.date_posted)).filter(Post.date_posted != None)
                top_month_query = month_query.order_by(desc('count')).first()
                bottom_month_query = month_query.order_by('count').first()
                dow_query = session.query(func.count(Post.id).label('count'),
                                          extract('dow', Post.date_posted).label('dow')) \
                    .group_by(extract('dow', Post.date_posted)).filter(Post.date_posted != None)
                top_dow_query = dow_query.order_by(desc('count')).first()
                bottom_dow_query = dow_query.order_by('count').first()
                year_query = session.query(func.count(Post.id).label('count'),
                                           extract('year', Post.date_posted).label('year')) \
                    .group_by(extract('year', Post.date_posted)).filter(Post.date_posted != None)
                top_year_query = year_query.order_by(desc('count')).first()
                bottom_year_query = year_query.order_by('count').first()

                extraction_date_query = session.query(func.count(Post.id).label('count'),
                                                      func.DATE(Post.extraction_date).label('date')) \
                    .group_by(func.DATE(Post.extraction_date)).filter(Post.extraction_date != None)
                most_extracted_date = extraction_date_query.order_by(desc('count')).first()
                least_extracted_date = extraction_date_query.order_by('count').first()
                extraction_month_query = session.query(func.count(Post.id).label('count'),
                                                       extract('month', Post.extraction_date).label('month')) \
                    .group_by(extract('month', Post.extraction_date)).filter(Post.extraction_date != None)
                most_extracted_month = extraction_month_query.order_by(desc('count')).first()
                least_extracted_month = extraction_month_query.order_by('count').first()
                dow_extraction = session.query(func.count(Post.id).label('count'),
                                               extract('dow', Post.extraction_date).label('dow')) \
                    .group_by(extract('dow', Post.extraction_date)).filter(Post.extraction_date != None)
                top_dow_extraction = dow_extraction.order_by(desc('count')).first()
                bottom_dow_extraction = dow_extraction.order_by('count').first()

                content_count_sub = session.query(func.count(Content.id).label('count')) \
                    .group_by(Content.post_id).subquery()
                min_content_count = session.query(func.min(content_count_sub.c.count)).first()[0]
                max_content_count = session.query(func.max(content_count_sub.c.count)).first()[0]
                avg_content_count = session.query(func.avg(content_count_sub.c.count)).first()[0]

                self.post_map = [
                    ('Total Posts', post_count),
                    ('Total Extracted Posts', session.query(Post.id).filter(Post.extracted == True).count()),
                    ('Total NSFW Posts',
                        f'{self.format_number(nsfw_post_count)}  '
                        f'({self.get_percentage(nsfw_post_count, post_count)} of all posts)'),
                    ('Total Non-NSFW Posts',
                        f'{self.format_number(non_nsfw_post_count)}  '
                        f'({self.get_percentage(non_nsfw_post_count, post_count)} of all posts)'),
                    ('Number of Self Posts',
                        f'{self.format_number(self_post_count)}  '
                        f'({self.get_percentage(self_post_count, post_count)} of all posts)'),
                    ('Total Score', total_score),
                    ('Highest Score', session.query(func.max(Post.score)).first()[0]),
                    ('Lowest Score', session.query(func.min(Post.score)).first()[0]),
                    ('Average Score', round(session.query(func.avg(Post.score)).first()[0])),
                    ('Most Common Title', self.get(common_title_query, 'title')),
                    ('Times Title Used', self.get(common_title_query, 'count')),
                    ('Total Unique Post Domains', total_domains),
                    ('Most Common Domain', self.get(domain_query, 'domain')),
                    ('Posts From Domain',
                        f'{self.format_number(self.get(domain_query, "count"))}  '
                        f'({self.get_percentage(self.get(domain_query, "count"), post_count)} of all posts)'),

                    ('SEPARATOR', None),
                    ('Oldest Post by Extraction',
                     f'Title: {self.get(oldest_extracted_post, "title")}\nAuthor: {oldest_extracted_post.author.name}'),
                    ('Oldest Extraction Date', self.get(oldest_extracted_post, 'extraction_date')),
                    ('Newest Post by Extraction',
                     f'Title: {self.get(newest_extracted_post, "title")}\n'
                     f'Author: {self.get(newest_extracted_post, "author.name")}'),
                    ('Newest Extraction Date', self.get(newest_extracted_post, 'extraction_date')),
                    ('Oldest Post by Post Date',
                     f'Title: {self.get(oldest_posted_post, "title")}\n'
                     f'Author: {self.get(oldest_posted_post, "author.name")}'),
                    ('Oldest Post Date', self.get(oldest_posted_post, 'date_posted')),
                    ('Newest Post by Post Date',
                     f'Title: {self.get(newest_posted_post, "title")}\n'
                     f'Author: {self.get(newest_posted_post, "author.name")}'),
                    ('Newest Post Date', self.get(newest_posted_post, 'date_posted')),

                    ('SEPARATOR', None),
                    ('Posts With Errors',
                        f'{self.format_number(error_count)}  '
                        f'({self.get_percentage(error_count, post_count)} of all posts)'),
                    ('Most Common Error', self.get(common_error_query, 'error') if common_error_query is not None else 'None'),
                    ('Times Error Encountered',
                     f'{self.format_number(self.get(common_error_query, "count"))}  '
                     f'({self.get_percentage(self.get(common_error_query, "count"), error_count)} of errors)'),
                    ('Least Common Error', self.get(least_common_error_query, 'error')),
                    ('Times Error Encountered',
                     f'{self.format_number(self.get(least_common_error_query, "count"))}  '
                     f'({self.get_percentage(self.get(least_common_error_query, "count"), error_count)} of errors)'),

                    ('SEPARATOR', None),
                    ('SUB_HEADER', 'Post Dates:'),
                    ('Most Posted Date', self.format_date_string(self.get(most_posted_date, 'date'))),
                    ('Posts That Day',
                     f'{self.format_number(self.get(most_posted_date, "count"))}  '
                     f'({self.get_percentage(self.get(most_posted_date, "count"), post_count)})'),
                    ('Least Posted Day', self.format_date_string(self.get(least_posted_date, 'date'))),
                    ('Posts That Day',
                     f'{self.format_number(self.get(least_posted_date, "count"))}  '
                     f'({self.get_percentage(self.get(least_posted_date, "count"), post_count)})'),
                    ('Most Common Post Month', calendar.month_name[top_month_query.month]),
                    ('Posts That Month',
                     f'{self.format_number(self.get(top_month_query, "count"))}  '
                     f'({self.get_percentage(self.get(top_month_query, "count"), post_count)})'),
                    ('Least Common Post Month', calendar.month_name[bottom_month_query.month]),
                    ('Posts That Month',
                     f'{self.format_number(self.get(bottom_month_query, "count"))}  '
                     f'({self.get_percentage(self.get(bottom_month_query, "count"), post_count)})'),
                    ('Most Popular Day of The Week', calendar.day_name[top_dow_query.dow]),
                    ('Posts That Day',
                     f'{self.format_number(self.get(top_dow_query, "count"))}  '
                     f'({self.get_percentage(self.get(top_dow_query, "count"), post_count)})'),
                    ('Least Popular Day of The Week', calendar.day_name[bottom_dow_query.dow]),
                    ('Posts That Day',
                     f'{self.format_number(self.get(bottom_dow_query, "count"))}  '
                     f'({self.get_percentage(self.get(bottom_dow_query, "count"), post_count)})'),
                    ('Most Common Post Year', str(top_year_query.year)),
                    ('Posts That Year',
                     f'{self.format_number(self.get(top_year_query, "count"))}  '
                     f'({self.get_percentage(self.get(top_year_query, "count"), post_count)})'),
                    ('Least Common Year', str(self.get(top_year_query, "year"))),
                    ('Posts That Year',
                     f'{self.format_number(self.get(bottom_year_query, "count"))}  '
                     f'({self.get_percentage(self.get(bottom_year_query, "count"), post_count)})'),

                    ('SEPARATOR', None),
                    ('SUB_HEADER', 'Extraction Dates:'),
                    ('Most Extracted Date', self.format_date_string(self.get(most_extracted_date, 'date'))),
                    ('Extracted That Day',
                     f'{self.format_number(self.get(most_extracted_date, "count"))}  '
                     f'({self.get_percentage(self.get(most_extracted_date, "count"), post_count)})'),
                    ('Least Extracted Date', self.format_date_string(self.get(least_extracted_date, 'date'))),
                    ('Extracted That Day',
                     f'{self.format_number(self.get(least_extracted_date, "count"))}  '
                     f'({self.get_percentage(self.get(least_extracted_date, "count"), post_count)}'),
                    ('Most Extracted Month', calendar.month_name[self.get(most_extracted_month, 'month')]),
                    ('Extractions That Month',
                     f'{self.format_number(self.get(most_extracted_month, "count"))}  '
                     f'({self.get_percentage(self.get(most_extracted_month, "count"), post_count)})'),
                    ('Least Extracted Month', calendar.month_name[self.get(least_extracted_month, "month")]),
                    ('Extractions That Month',
                     f'{self.format_number(self.get(least_extracted_month, "count"))}  '
                     f'({self.get_percentage(self.get(least_extracted_month, "count"), post_count)})'),
                    ('Most Extracted Day of The Week', calendar.day_name[self.get(top_dow_extraction, 'dow')]),
                    ('Posts That Day',
                     f'{self.format_number(self.get(top_dow_extraction, "count"))}  '
                     f'({self.get_percentage(self.get(top_dow_extraction, "count"), post_count)})'),
                    ('Least Extracted Day of The Week', calendar.day_name[self.get(bottom_dow_extraction, 'dow')]),
                    ('Posts That Day',
                     f'{self.format_number(self.get(bottom_dow_extraction, "count"))}  '
                     f'({self.get_percentage(self.get(bottom_dow_extraction, "count"), post_count)})'),

                    ('SEPARATOR', None),
                    ('Fewest Content From Post', min_content_count),
                    ('Most Content From Post', max_content_count),
                    ('Average Content Per Post', round(avg_content_count)),
                ]

                content_count = session.query(Content.id).count()
                downloaded_content_count = session.query(Content.id).filter(Content.downloaded == True).count()

                content_exts = session.query(func.count(Content.id).label('count'), Content.extension.label('ext')) \
                    .group_by(Content.extension).filter(Content.extension != None)
                most_used_extension = content_exts.order_by(desc('count')).first()
                least_used_extension = content_exts.order_by('count').first()

                content_from_posts = session.query(Content.id).filter(Content.comment_id == None).count()

                download_error_count = session.query(Content.id).filter(Content.download_error != None).count()
                content_error_base = session.query(func.count(Content.id).label('count'),
                                                   Content.download_error.label('error')) \
                    .filter(Content.download_error != None)
                content_error_aggregate = content_error_base.group_by(Content.download_error)
                common_download_error_query = content_error_aggregate.order_by(desc('count')).first()
                least_common_download_error_query = content_error_aggregate.order_by('count').first()

                content_date_query = session.query(func.count(Content.id).label('count'),
                                                   func.DATE(Content.download_date).label('date')) \
                    .group_by(func.DATE(Content.download_date)).filter(Content.download_date != None)
                most_downloaded_date = content_date_query.order_by(desc('count')).first()
                least_downloaded_date = content_date_query.order_by('count').first()
                content_month_query = session.query(func.count(Content.id).label('count'),
                                                    extract('month', Content.download_date).label('month')) \
                    .group_by(extract('month', Content.download_date)).filter(Content.download_date != None)
                content_top_month_query = content_month_query.order_by(desc('count')).first()
                content_bottom_month_query = content_month_query.order_by('count').first()
                content_dow_query = session.query(func.count(Content.id).label('count'),
                                                  extract('dow', Content.download_date).label('dow')) \
                    .group_by(extract('dow', Content.download_date)).filter(Content.download_date != None)
                content_top_dow_query = content_dow_query.order_by(desc('count')).first()
                content_bottom_dow_query = content_dow_query.order_by('count').first()
                content_year_query = session.query(func.count(Content.id).label('count'),
                                                   extract('year', Content.download_date).label('year')) \
                    .group_by(extract('year', Content.download_date)).filter(Content.download_date != None)
                content_top_year = content_year_query.order_by(desc('count')).first()
                content_bottom_year = content_year_query.order_by('count').first()

                self.content_map = [
                    ('Total Content', content_count),
                    ('Downloaded Content', f'{self.format_number(downloaded_content_count)} '
                                           f'({self.get_percentage(downloaded_content_count, content_count)})'),
                    ('Content Not Downloaded\n(non-error)',
                        f'{content_count - downloaded_content_count} '
                        f'({self.get_percentage((content_count - downloaded_content_count), content_count)})'),
                    ('SEPARATOR', None),
                    ('Most Common Extension', self.get(most_used_extension, 'ext')),
                    ('Extension Used',
                     f'{self.format_number(self.get(most_used_extension, "count"))}  '
                     f'({self.get_percentage(self.get(most_used_extension, "count"), content_count)})'),
                    ('Least Common Extension', self.get(least_used_extension, 'ext')),
                    ('Extension Used',
                     f'{self.format_number(self.get(least_used_extension, "count"))}  '
                     f'({self.get_percentage(self.get(least_used_extension, "count"), content_count)})'),

                    ('SEPARATOR', None),
                    ('Content From Posts',
                        f'{self.format_number(content_from_posts)}  '
                        f'({self.get_percentage(content_from_posts, content_count)})'),
                    ('Content From Comments',
                        f'{self.format_number(content_count - content_from_posts)}  '
                        f'({self.get_percentage(content_count - content_from_posts, content_count)})'),

                    ('SEPARATOR', None),
                    ('Download Errors', download_error_count),
                    ('Most Common Error', self.get(common_download_error_query, 'error')),
                    ('Times Encountered', self.get(common_download_error_query, 'count')),
                    ('Least Common Error', self.get(least_common_download_error_query, 'error')),
                    ('Times Encountered', self.get(least_common_download_error_query, 'count')),

                    ('SEPARATOR', None),
                    ('SUB_HEADER', 'Download Dates:'),
                    ('Most Downloaded Date', self.format_date_string(self.get(most_downloaded_date, 'date'))),
                    ('Downloaded on This Date',
                     f'{self.format_number(self.get(most_downloaded_date, "count"))}  '
                     f'({self.get_percentage(self.get(most_downloaded_date, "count"), content_count)})'),
                    ('Least Downloaded Date', self.format_date_string(self.get(least_downloaded_date, 'date'))),
                    ('Downloaded on This Date',
                     f'{self.format_number(self.get(least_downloaded_date, "count"))}  '
                     f'({self.get_percentage(self.get(least_downloaded_date, "count"), content_count)})'),
                    ('Most Common Download Month', calendar.month_name[self.get(content_top_month_query, 'month')]),
                    ('Downloads That Month',
                     f'{self.format_number(self.get(content_top_month_query, "count"))}  '
                     f'({self.get_percentage(self.get(content_top_month_query, "count"), content_count)})'),
                    ('Least Common Download Month', calendar.month_name[self.get(content_bottom_month_query, 'month')]),
                    ('Downloads That Month',
                     f'{self.format_number(self.get(content_bottom_month_query, "count"))}  '
                     f'({self.get_percentage(self.get(content_bottom_month_query, "count"), content_count)})'),
                    ('Most Popular Day of The Week', calendar.day_name[self.get(content_top_dow_query, 'dow')]),
                    ('Downloads That Day', f'{self.format_number(self.get(content_top_dow_query, "count"))}  '
                                           f'({self.get_percentage(self.get(content_top_dow_query, "count"), content_count)})'),
                    ('Least Popular Day of The Week', calendar.day_name[self.get(content_bottom_dow_query, 'dow')]),
                    ('Downloads That Day',
                     f'{self.format_number(self.get(content_bottom_dow_query, "count"))}  '
                     f'({self.get_percentage(self.get(content_bottom_dow_query, "count"), content_count)})'),
                    ('Most Common Download Year', str(self.get(content_top_year, 'year'))),
                    ('Downloads That Year', f'{self.format_number(self.get(content_top_year, "count"))}  '
                                            f'({self.get_percentage(self.get(content_top_year, "count"), content_count)})'),
                    ('Least Common Download Year', str(self.get(content_bottom_year, 'year'))),
                    ('Downloads That Year', f'{self.format_number(self.get(content_bottom_year, "count"))}  '
                                            f'({self.get_percentage(self.get(content_bottom_year, "count"), content_count)})')
                ]

                session_count = session.query(DownloadSession.id).count()
                completed_sessions = session.query(DownloadSession.id).filter(DownloadSession.end_time != None).count()
                incomplete_sessions = session_count - completed_sessions
                oldest_session = session.query(DownloadSession).order_by(DownloadSession.start_time).first()
                newest_session = session.query(DownloadSession).order_by(desc(DownloadSession.start_time)).first()
                session_post_extraction = session.query(func.count(Post.download_session_id).label('count')) \
                    .group_by(Post.download_session_id)
                most_extracted = session_post_extraction.order_by(desc('count')).first()[0]
                least_extracted = session_post_extraction.order_by('count').first()[0]
                session_content_download = session.query(func.count(Content.download_session_id).label('count')) \
                    .group_by(Content.download_session_id)
                most_downloaded = session_content_download.order_by(desc('count')).first()[0]
                least_downloaded = session_content_download.order_by('count').first()[0]

                shortest_download_session = session.query(DownloadSession).filter(DownloadSession.duration != None) \
                    .filter(DownloadSession.duration >= 0).order_by(DownloadSession.duration).first()
                longest_download_session = session.query(DownloadSession).filter(DownloadSession.duration != None) \
                    .filter(DownloadSession.duration >= 0).order_by(desc(DownloadSession.duration)).first()

                run_date_query = session.query(func.count(DownloadSession.id).label('count'),
                                               func.DATE(DownloadSession.start_time).label('date')) \
                    .group_by(func.DATE(DownloadSession.start_time)).filter(DownloadSession.start_time != None)
                most_run_date = run_date_query.order_by(desc('count')).first()
                least_run_date = run_date_query.order_by('count').first()
                run_month_query = session.query(func.count(DownloadSession.id).label('count'),
                                                extract('month', DownloadSession.start_time).label('month')) \
                    .group_by(extract('month', DownloadSession.start_time)).filter(DownloadSession.start_time != None)
                most_run_month = run_month_query.order_by(desc('count')).first()
                least_run_month = run_month_query.order_by('count').first()
                run_dow_query = session.query(func.count(DownloadSession.id).label('count'),
                                              extract('dow', DownloadSession.start_time).label('dow')) \
                    .group_by(extract('dow', DownloadSession.start_time)).filter(DownloadSession.start_time != None)
                top_run_dow = run_dow_query.order_by(desc('count')).first()
                bottom_run_dow = run_dow_query.order_by('count').first()

                self.download_sessions_map = [
                    ('Total Download Sessions', session_count),
                    ('Completed Sessions',
                        f'{self.format_number(completed_sessions)}  '
                        f'({self.get_percentage(completed_sessions, session_count)})'),
                    ('Incomplete Sessions',
                        f'{self.format_number(incomplete_sessions)}  '
                        f'({self.get_percentage(incomplete_sessions, session_count)})'),
                    ('Oldest Session', self.get(oldest_session, 'name')),
                    ('Run Date', self.get(oldest_session, 'start_time')),
                    ('Newest Session', self.get(newest_session, 'name')),
                    ('Run Date', self.get(newest_session, 'start_time')),
                    ('Most Extracted Posts', most_extracted),
                    ('Least Extracted Posts', least_extracted),
                    ('Most Downloaded Content', most_downloaded),
                    ('Least Downloaded Content', least_downloaded),

                    ('SEPARATOR', None),
                    ('Average Download Time',
                     system_util.format_duration_full(session.query(func.avg(DownloadSession.duration))
                                                      .filter(DownloadSession.duration >= 0).first()[0])),
                    ('Shortest Download Session', self.get(shortest_download_session, 'name')),
                    ('Shorted Download Time',
                     system_util.format_duration_full(self.get(shortest_download_session, 'duration'))),
                    ('Posts Extracted', session.query(Post.id)
                     .filter(Post.download_session_id == shortest_download_session.id)
                     .filter(Post.extracted == True).count()),
                    ('Content Downloaded', session.query(Content.id)
                     .filter(Content.download_session_id == shortest_download_session.id)
                     .filter(Content.downloaded == True).count()),
                    ('Longest Download Session', longest_download_session.name),
                    ('Longest Download Time', system_util.format_duration_full(longest_download_session.duration)),
                    ('Posts Extracted', session.query(Post.id)
                     .filter(Post.download_session_id == longest_download_session.id)
                     .filter(Post.extracted == True).count()),
                    ('Content Downloaded', session.query(Content.id)
                     .filter(Content.download_session_id == longest_download_session.id)
                     .filter(Content.downloaded == True).count()),

                    ('SEPARATOR', None),
                    ('Most Run Date', self.format_date_string(self.get(most_run_date, 'date'))),
                    ('Runs On This Date',
                        f'{self.format_number(self.get(most_run_date, "count"))}  '
                        f'({self.get_percentage(self.get(most_run_date, "count"), session_count)})'),
                    ('Least Run Date', self.format_date_string(self.get(least_run_date, 'date'))),
                    ('Runs On This Date',
                        f'{self.format_number(self.get(least_run_date, "count"))}  '
                        f'({self.get_percentage(self.get(least_run_date, "count"), session_count)})'),
                    ('Most Run Month', calendar.month_name[self.get(most_run_month, 'month')]),
                    ('Runs That Month',
                        f'{self.format_number(self.get(most_run_month, "count"))}  '
                        f'({self.get_percentage(self.get(most_run_month, "count"), session_count)})'),
                    ('Least Run Month', calendar.month_name[self.get(least_run_month, 'month')]),
                    ('Runs That Month',
                        f'{self.format_number(self.get(least_run_month, "count"))}  '
                        f'({self.get_percentage(self.get(least_run_month, "count"), session_count)})'),
                    ('Most Run Day of The Week', calendar.day_name[self.get(top_run_dow, 'dow')]),
                    ('Runs This Day',
                        f'{self.format_number(self.get(top_run_dow, "count"))}  '
                        f'({self.get_percentage(self.get(top_run_dow, "count"), session_count)})'),
                    ('Least Run Day of The Week', calendar.day_name[self.get(bottom_run_dow, 'dow')]),
                    ('Runs This Day',
                        f'{self.format_number(self.get(bottom_run_dow, "count"))}  '
                        f'({self.get_percentage(self.get(bottom_run_dow, "count"), session_count)})')
                ]

                self.item_count = self.format_number(self.get_total_row_count(session))
                self.database_size = system_util.format_size(os.path.getsize(self.db.database_path))

                self.database_map = [
                    ('Total Items In Database', self.item_count),
                    ('Database File Size', self.database_size),
                ]

                self.setup_ui()

                end_time = time()
                self.logger.info('Database statistics calculated', extra={'total_stats': self.stat_count,
                                                                          'setup_time': round(end_time - start_time, 3),
                                                                          'total_items': self.item_count,
                                                                          'database_file_size': self.database_size})

        except:
            item_count = self.get_total_row_count(session)
            self.logger.error('Failed to load database statistics', extra={'total_database_items': item_count},
                              exc_info=True)
            if item_count == 0:
                text = 'No items in database.'
            else:
                text = 'Unknown error'
            label = QLabel(f'No statistics currently available.  {text}')
            self.stat_layout.addWidget(label)

    def get(self, query, attr):
        try:
            a = attrgetter(attr)
            return a(query)
        except AttributeError:
            return None

    def get_percentage(self, x, y):
        """
        Returns the percentage X is of Y as a string.
        :param x: The smaller number which is some percentage of Y.
        :param y: The larger number of which X represents some percentage of.
        :return: X percent of Y as a string.
        """
        try:
            return f'{round((x / y) * 100, 2)}%'
        except ZeroDivisionError:
            return '0%'
        except TypeError:
            return None

    def setup_ui(self):
        self.add_separator('Users/Subreddits', False)
        self.add_layout_from_map(self.reddit_object_map)
        self.add_separator('Users', True, heavy=True)
        self.add_layout_from_map(self.user_map)
        self.add_separator('Subreddits', True, heavy=True)
        self.add_layout_from_map(self.subreddit_map)
        self.add_separator('Lists', True, heavy=True)
        self.add_layout_from_map(self.list_map)
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
        for item in item_map:
            if len(item) == 3:
                key, value, tooltip = item
            else:
                key, value = item
                tooltip = None

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
                    value = general_utils.format_datetime(value)
                key_label = QLabel(key + ':')
                value_label = QLabel(str(value))
                if tooltip is not None:
                    key_label.setToolTip(tooltip)
                    key_label.setWhatsThis(tooltip)
                    value_label.setToolTip(tooltip)
                    value_label.setWhatsThis(tooltip)
                layout.addRow(key_label, value_label)
                self.stat_count += 1
            row += 1
        self.stat_layout.addWidget(widget)

    def format_number(self, number):
        try:
            return '{:,}'.format(number)
        except (TypeError, AttributeError):
            return None

    def format_date_string(self, date_string):
        date = datetime.strptime(date_string, '%Y-%m-%d').date()
        return general_utils.format_date(date)

    def get_user_content_count_sub(self, session, ext):
        return session.query(Content.user_id, func.count(Content.id).label('count')) \
            .filter(Content.extension.in_(self.get_ext(ext))).group_by(Content.user_id).subquery()

    def get_subreddit_content_count_sub(self, session, ext):
        return session.query(Content.subreddit_id, func.count(Content.id).label('count')) \
            .filter(Content.extension.in_(self.get_ext(ext))).group_by(Content.subreddit_id).subquery()

    def get_user_extension_query(self, session, ext):
        sub = self.get_user_content_count_sub(session, ext)
        return session.query(User, 'count').outerjoin(sub, sub.c.user_id == User.id).order_by(desc('count')).first()

    def get_sub_extension_query(self, session, ext):
        sub = self.get_subreddit_content_count_sub(session, ext)
        return session.query(Subreddit, 'count').outerjoin(sub, sub.c.subreddit_id == Subreddit.id) \
            .order_by(desc('count')).first()

    def get_ext(self, ext_type):
        if ext_type == 'IMG':
            t = const.IMAGE_EXT
        elif ext_type == 'VID':
            t = const.VID_EXT
        else:
            t = const.GIF_EXT
        return t

    def get_total_row_count(self, session):
        count = 0
        for model in [RedditObject, DownloadSession, RedditObjectList, ListAssociation, Post, Content, Comment]:
            count += session.query(model.id).count()
        return count

    def closeEvent(self, event):
        self.settings_manager.database_statistics_geom = {
            'width': self.width(),
            'height': self.height(),
            'x': self.x(),
            'y': self.y()
        }
