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

import logging
from time import time
import requests

from ..utils import injector


logger = logging.getLogger(__name__)

_FREE_ENDPOINT = 'https://api.imgur.com/3/'
_RAPID_API_ENDPOINT = 'https://imgur-apiv3.p.rapidapi.com/3/'

credit_reset_time = 0
num_credits = 0


class ImgurError(Exception):

    def __init__(self, status_code):
        self.status_code = status_code


def _send_request(url_extension, retries=1):
    global num_credits
    if retries < 0:
        return
    headers = {
        'Authorization': 'Client-ID {}'.format(injector.settings_manager.imgur_client_id)
    }
    if time() > credit_reset_time:
        check_credits()
    if num_credits > 0:
        url = _FREE_ENDPOINT + url_extension
        num_credits -= 1
    elif injector.settings_manager.imgur_mashape_key is not None:
        url = _RAPID_API_ENDPOINT + url_extension
        headers['X-Mashape-Key'] = injector.settings_manager.imgur_mashape_key
    else:
        raise ImgurError(429)
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
        return response.json()
    if response.status_code == 429:
        # Rate limiting.
        check_credits()
        _send_request(url_extension, retries - 1)
    raise ImgurError(response.status_code)


def check_credits():
    global num_credits, credit_reset_time
    url = _FREE_ENDPOINT + "credits"
    headers = {
        'Authorization': 'Client-ID {}'.format(injector.settings_manager.imgur_client_id)
    }
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code != 200:
        logger.error('Failed to check imgur credits, bad status code', extra={'status_code': response.status_code},
                     exc_info=True)
    else:
        result = response.json()
        credits_data = result['data']
        num_credits = min(credits_data['UserRemaining'], credits_data['ClientRemaining'])
        credit_reset_time = credits_data['UserReset']
        return num_credits


def get_link(json):
    if json['animated']:
        return json['mp4']
    return json['link']


def get_album_images(album_id):
    json = _send_request('album/{}/images'.format(album_id))
    data = json['data']
    urls = [get_link(x) for x in data]
    return urls


def get_single_image(image_id):
    json = _send_request('image/{}'.format(image_id))
    data = json['data']
    return get_link(data)
