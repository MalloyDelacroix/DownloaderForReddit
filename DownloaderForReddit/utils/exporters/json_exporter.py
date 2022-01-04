"""
Downloader for Reddit takes a list of reddit users and subreddits and downloads content posted to reddit either by the
users or on the subreddits.


Copyright (C) 2017, Kyle Hickey


This file is part of the Downloader for Reddit.

Downloader for Reddit is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Downloader for Reddit is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Downloader for Reddit.  If not, see <http://www.gnu.org/licenses/>.
"""

import json
import logging

from ...database.models import RedditObjectList, RedditObject, Post, Content, Comment


logger = logging.getLogger(__name__)


class RedditObjectListCollection:

    def __init__(self, object_list):
        self.reddit_object_lists = object_list if isinstance(object_list, list) else [object_list]

    def size(self):
        return len(self.reddit_object_lists)


class SimpleJSONRedditObjectListEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, RedditObjectList):
            return {
                'id': o.id,
                'name': o.name,
                'date_created': o.date_created_export,
                'list_type': o.list_type,
                'lock_settings': o.lock_settings,
                'post_limit': o.post_limit,
                'post_score_limit': o.post_score_limit,
                'post_score_limit_operator': o.post_score_limit_operator.value,
                'post_sort_method': o.post_sort_method.value,
                'avoid_duplicates': o.avoid_duplicates,
                'extract_self_post_links': o.extract_self_post_links,
                'download_self_post_text': o.download_self_post_text,
                'self_post_file_format': o.self_post_file_format,
                'download_videos': o.download_videos,
                'download_images': o.download_images,
                'download_gifs': o.download_gifs,
                'download_nsfw': o.download_nsfw.value,
                'extract_comments': o.extract_comments.value,
                'download_comments': o.download_comments.value,
                'download_comment_content': o.download_comment_content.value,
                'comment_file_format': o.comment_file_format,
                'comment_limit': o.comment_limit,
                'comment_score_limit': o.comment_score_limit,
                'comment_score_limit_operator': o.comment_score_limit_operator.value,
                'comment_sort_method': o.comment_sort_method.value,
                'date_limit': o.date_limit_export,
                'post_download_naming_method': o.post_download_naming_method,
                'post_save_structure': o.post_save_structure,
                'comment_naming_method': o.comment_naming_method,
                'comment_save_structure': o.comment_save_structure,
                'download_enabled': o.download_enabled,
                'absolute_date_limit': o.absolute_date_limit_export,
            }


class NestedJSONRedditObjectListEncoder(SimpleJSONRedditObjectListEncoder):

    def default(self, o):
        if isinstance(o, RedditObjectList):
            data = super().default(o)
            data['reddit_objects'] = json.loads(json.dumps(o.reddit_objects.all(), cls=NestedJSONRedditObjectEncoder))
            return data


class RedditObjectCollection:

    def __init__(self, object_list):
        self.reddit_objects = object_list

    def size(self):
        return len(self.reddit_objects)


class SimpleJSONRedditObjectEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, RedditObject):
            return {
                'id': o.id,
                'name': o.name,
                'date_created': o.date_created_export,
                'post_limit': o.post_limit,
                'post_score_limit': o.post_score_limit,
                'post_score_limit_operator': o.post_score_limit_operator.value,
                'post_sort_method': o.post_sort_method.value,
                'avoid_duplicates': o.avoid_duplicates,
                'extract_self_post_links': o.extract_self_post_links,
                'download_self_post_text': o.download_self_post_text,
                'self_post_file_format': o.self_post_file_format,
                'download_videos': o.download_videos,
                'download_images': o.download_images,
                'download_gifs': o.download_gifs,
                'download_nsfw': o.download_nsfw.value,
                'extract_comments': o.extract_comments.value,
                'download_comments': o.download_comments.value,
                'download_comment_content': o.download_comment_content.value,
                'comment_file_format': o.comment_file_format,
                'comment_limit': o.comment_limit,
                'comment_score_limit': o.comment_score_limit,
                'comment_score_limit_operator': o.comment_score_limit_operator.value,
                'comment_sort_method': o.comment_sort_method.value,
                'date_added': o.date_added_export,
                'lock_settings': o.lock_settings,
                'absolute_date_limit': o.absolute_date_limit_export,
                'date_limit': o.date_limit_export,
                'download_enabled': o.download_enabled,
                'significant': o.significant,
                'active': o.active,
                'inactive_date': o.inactive_date,
                'post_download_naming_method': o.post_download_naming_method,
                'post_save_structure': o.post_save_structure,
                'comment_naming_method': o.comment_naming_method,
                'comment_save_structure': o.comment_save_structure,
                'new': o.new,
                'object_type': o.object_type,
            }


class NestedJSONRedditObjectEncoder(SimpleJSONRedditObjectEncoder):

    def default(self, o):
        if isinstance(o, RedditObject):
            data = super().default(o)
            data['posts'] = json.loads(json.dumps(o.posts, cls=SimpleJSONPostEncoder))
            data['content'] = json.loads(json.dumps(o.content, cls=SimpleJSONContentEncoder))
            data['comments'] = json.loads(json.dumps(o.comments, cls=SimpleJSONCommentEncoder))
            data['lists'] = [{'id': l.id, 'name': l.name} for l in o.lists]
            return data


class PostCollection:

    def __init__(self, post_list):
        self.posts = post_list

    def size(self):
        return len(self.posts)


class SimpleJSONPostEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, Post):
            return {
                'id': o.id,
                'title': o.title,
                'score': o.score,
                'reddit_id': o.reddit_id,
                'nsfw': o.nsfw,
                'date_posted': o.date_posted_export,
                'url': o.url,
                'is_self': o.is_self,
                'text': o.text,
                'text_html': o.text_html,
                'extracted': o.extracted,
                'extraction_date': o.extraction_date_export,
                'extraction_error': o.extraction_error.name if o.extraction_error else None,
                'download_session_id': o.download_session_id,
                'author_id': o.author_id,
                'author': o.author.name if o.author is not None else None,
                'subreddit_id': o.subreddit_id,
                'subreddit': o.subreddit.name if o.subreddit is not None else None,
                'content': [c.id for c in o.content],
                'comments': [comment.id for comment in o.comments]
            }
        return json.JSONEncoder.default(self, o)


class NestedJSONPostEncoder(SimpleJSONPostEncoder):

    def default(self, o):
        if isinstance(o, Post):
            data = super().default(o)
            data['author'] = json.loads(json.dumps(o.author, cls=SimpleJSONRedditObjectEncoder))
            data['subreddit'] = json.loads(json.dumps(o.subreddit, cls=SimpleJSONRedditObjectEncoder))
            return data


class CommentCollection:

    def __init__(self, comment_list):
        self.comment_list = comment_list

    def size(self):
        return len(self.comment_list)


class SimpleJSONCommentEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, Comment):
            return {
                'id': o.id,
                'body': o.body,
                'body_html': o.body_html,
                'score': o.score_display,
                'date_added': o.date_added_export,
                'date_posted': o.date_posted_export,
                'reddit_id': o.reddit_id,
                'extracted': o.extracted,
                'extraction_date': o.extraction_date_export,
                'extraction_error': o.extraction_error.name if o.extraction_error else None,
                'retry_attempts': o.retry_attempts,
                'author_id': o.author_id,
                'author': o.author.name if o.author is not None else None,
                'subreddit_id': o.subreddit_id,
                'subreddit': o.subreddit.name if o.subreddit is not None else None,
                'post_id': o.post_id,
                'post': o.post_title,
                'content': [c.id for c in o.content],
                'download_session_id': o.download_session_id
            }
        return json.JSONEncoder.default(self, o)


class NestedJSONCommentEncoder(SimpleJSONCommentEncoder):

    def default(self, o):
        if isinstance(o, Comment):
            data = super().default(o)
            data['author'] = json.loads(json.dumps(o.author, cls=SimpleJSONRedditObjectEncoder))
            data['subreddit'] = json.loads(json.dumps(o.subreddit, cls=SimpleJSONRedditObjectEncoder))
            data['post'] = json.loads(json.dumps(o.post, cls=SimpleJSONPostEncoder))
            return data


class ContentCollection:

    def __init__(self, content_list):
        self.content_list = content_list

    def size(self):
        return len(self.content_list)


class SimpleJSONContentEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, Content):
            return {
                'id': o.id,
                'title': o.title,
                'download_title': o.download_title,
                'extension': o.extension,
                'url': o.url,
                'directory_path': o.directory_path,
                'downloaded': o.downloaded,
                'download_date': o.download_date_export,
                'download_error': o.download_error.name if o.download_error else None,
                'retry_attempts': o.retry_attempts,
                'user_id': o.user_id,
                'user': o.user.name if o.user is not None else None,
                'subreddit_id': o.subreddit_id,
                'subreddit': o.subreddit.name if o.subreddit is not None else None,
                'post_id': o.post_id,
                'post_reddit_id': o.post.reddit_id if o.post is not None else None,
                'comment_id': o.comment_id,
                'download_session_id': o.download_session_id
            }
        return json.JSONEncoder.default(self, o)


class NestedJSONContentEncoder(SimpleJSONContentEncoder):

    def default(self, o):
        if isinstance(o, Content):
            data = super().default(o)
            data['user'] = json.loads(json.dumps(o.user, cls=SimpleJSONRedditObjectEncoder))
            data['subreddit'] = json.loads(json.dumps(o.subreddit, cls=SimpleJSONRedditObjectEncoder))
            data['post'] = json.loads(json.dumps(o.post, cls=SimpleJSONPostEncoder))
            data['comment'] = json.loads(json.dumps(o.comment, cls=SimpleJSONCommentEncoder))
            return data


def export_reddit_object_list_to_json(object_list, file_path, nested=False):
    encoder = NestedJSONRedditObjectListEncoder if nested else SimpleJSONRedditObjectListEncoder
    _export(RedditObjectListCollection(object_list), file_path, encoder)


def export_reddit_objects_to_json(object_list, file_path, nested=False):
    """
    Exports the reddit objects in the supplied object_list to a formatted json file.
    :param object_list: A list of RedditObjects which are to be exported to a json file.
    :param file_path: The path at which the json file will be created.
    :param nested: Dictates whether the encoder used to encode the data to json is a simple or nested encoder.
    """
    encoder = NestedJSONRedditObjectEncoder if nested else SimpleJSONRedditObjectEncoder
    _export(RedditObjectCollection(object_list), file_path, encoder)


def export_posts_to_json(post_list, file_path, nested=False):
    """
    Exports the posts in the supplied post_list to a formatted json file.
    :param post_list: A list of posts which are to be exported to a json file.
    :param file_path: The path at which the json file will be created.
    :param nested: Dictates whether the encoder used to encode the data to json is a simple or nested encoder.
    """
    encoder = NestedJSONPostEncoder if nested else SimpleJSONPostEncoder
    _export(PostCollection(post_list), file_path, encoder)


def export_content_to_json(content_list, file_path, nested=False):
    content_list = list(content_list)
    encoder = NestedJSONContentEncoder if nested else SimpleJSONContentEncoder
    _export(ContentCollection(content_list), file_path, encoder)


def export_comments_to_json(comment_list, file_path, nested=False):
    comment_list = list(comment_list)
    encoder = NestedJSONCommentEncoder if nested else SimpleJSONCommentEncoder
    _export(CommentCollection(comment_list), file_path, encoder)


def _export(collection, file_path, encoder):
    with open(file_path, mode='a', encoding='utf-8') as file:
        json.dump(collection.__dict__, file, cls=encoder, indent=4, ensure_ascii=False)
    logger.info(f'Exported {collection.__class__.__name__} to json file',
                extra={'encoder': encoder.__name__, 'export_count': collection.size()})
