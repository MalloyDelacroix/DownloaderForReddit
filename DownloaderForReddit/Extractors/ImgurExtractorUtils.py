import logging
from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError

from Core import Injector


logger = logging.getLogger(__name__)
imgur_client = None
connection_attempts = 0


def get_client():
    """
    Configures and returns the imgur_client for application use.  If an error is encountered, connection will be
    attempted 3 times, then the exception is re-raised be passed on to be handled by the calling method.
    :return: The imgur client for the various parts of the application to use in interacting with imgur.
    :rtype: ImgurClient
    """
    global imgur_client
    global connection_attempts

    Injector.get_queue().put('get client called')

    if not imgur_client:
        while connection_attempts < 3:
            try:
                client_id = Injector.settings_manager.imgur_client_id
                client_secret = Injector.settings_manager.imgur_client_secret
                imgur_client = ImgurClient(client_id, client_secret)
                connection_attempts = 0
                break
            except ImgurClientError as e:
                if e.status_code == 403 and e.error_message.startswith('Invalid client'):
                    handle_invalid_client()
                return None
            except Exception as e:
                if connection_attempts < 2:
                    connection_attempts += 1
                else:
                    raise e
    return imgur_client


def handle_invalid_client():
    message = 'No valid Imgur client detected.  In order to download content from imgur.com, you must ' \
              'have a valid imgur client id and client secret.  Please see the imgur client information' \
              'dialog in the settings menu.'
    Injector.get_queue().put(message)
    logger.warning('Invalid imgur client id or secret')
