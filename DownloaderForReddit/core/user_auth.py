import logging

from PyQt5.QtCore import QByteArray, QUrl, QObject, pyqtSignal
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtNetwork import QNetworkAccessManager
from PyQt5.QtNetworkAuth import QOAuthHttpServerReplyHandler, QOAuth2AuthorizationCodeFlow


class UaNetworkAccessManager(QNetworkAccessManager):
    """
    Handles network requests with a customizable User-Agent header.

    This class extends QNetworkAccessManager to allow setting a custom User-Agent header for all network requests.

    :ivar _ua: Encoded User-Agent string that will be added as a header in network requests.
    :type _ua: bytes
    """
    def __init__(self, user_agent: str, parent=None):
        super().__init__(parent)
        self._ua = user_agent.encode('utf-8')

    def createRequest(self, op, request, outgoingData=None):
        request.setRawHeader(QByteArray(b'User-Agent'), QByteArray(self._ua))
        return super().createRequest(op, request, outgoingData)


class UserAuth(QObject):
    """
    Handles user authentication using OAuth2 for Reddit API.

    This class provides functionality to initialize and manage the OAuth2 authentication process,
    including requesting user authorization, obtaining access tokens, and emitting signals upon
    successful or failed connection.

    :ivar connected: Signal emitted indicating authentication success or failure.
    :type connected: pyqtSignal
    :ivar reddit_utils: Utility object that provides required Reddit API details such as client ID,
        user agent, redirect URL, and token scopes.
    :type reddit_utils: RedditUtils
    :ivar client_id: The client ID required for Reddit OAuth2.
    :type client_id: str
    :ivar user_agent: The user agent string used in HTTP requests during OAuth2 flow.
    :type user_agent: str
    :ivar redirect_uri: Redirect URI used in the authentication process with Reddit.
    :type redirect_uri: str
    :ivar token_scope: A list of token scopes defining permissions granted during authentication.
    :type token_scope: list[str]
    :ivar authorization_url: URL used for initiating the Reddit authorization process.
    :type authorization_url: QUrl
    :ivar access_url: URL used for obtaining access tokens from Reddit.
    :type access_url: QUrl
    :ivar oauth: Instance of QOAuth2AuthorizationCodeFlow that manages the OAuth2 flow. Initialized
        during the authentication process.
    :type oauth: QOAuth2AuthorizationCodeFlow or None
    """
    connected = pyqtSignal(bool)

    def __init__(self, reddit_utils, parent=None):
        super().__init__(parent=parent)
        self.logger = logging.getLogger(f'DownloaderForReddit.{__name__}')
        self.reddit_utils = reddit_utils
        self.client_id = reddit_utils.CLIENT_ID
        self.user_agent = reddit_utils.USER_AGENT
        self.redirect_uri = reddit_utils.REDIRECT_URL
        self.token_scope = reddit_utils.TOKEN_SCOPES
        self.authorization_url = QUrl("https://www.reddit.com/api/v1/authorize")
        self.access_url = QUrl("https://www.reddit.com/api/v1/access_token")
        self.oauth = None

    def start_oauth(self):
        """
        Starts the OAuth 2.0 authorization process for the application. This involves setting up an authorization flow,
        configuring the required parameters, and initiating the authorization dialog using the appropriate
        web browser. The user is expected to grant access during the process.

        The function utilizes the QOAuth2AuthorizationCodeFlow class to handle the request and response cycle, while
        ensuring the necessary authentication details such as client ID, authorization URL, and access token URL
        are properly configured.

        :return: Instance of QOAuth2AuthorizationCodeFlow configured for the authorization process.
        :rtype: QOAuth2AuthorizationCodeFlow
        """
        manager = UaNetworkAccessManager(self.user_agent, self)
        reply_handler = QOAuthHttpServerReplyHandler(8086)
        oauth = QOAuth2AuthorizationCodeFlow(
            self.client_id,
            self.authorization_url,
            self.access_url,
            manager,
            self
        )

        oauth.granted.connect(self.finish_oauth)
        oauth.error.connect(
            lambda error, description: self.logger.error(f'OAuth error: {error} - {description}')
        )

        oauth.authorizeWithBrowser.connect(QDesktopServices.openUrl)
        oauth.setReplyHandler(reply_handler)
        oauth.setScope(" ".join(self.token_scope))
        oauth.setUserAgent(self.user_agent)

        params = {
            "duration": "permanent"
        }

        oauth.resourceOwnerAuthorization(self.authorization_url, params)
        self.oauth = oauth
        return oauth

    def finish_oauth(self):
        """
        Handles the finalization of the OAuth process by refreshing tokens, saving the resulting token,
        and emitting the connection status signal.

        :return: None
        """
        if not self.oauth:
            self.connected.emit(False)
            self.logger.error(
                'Failed to create OAuth (QOAuth2AuthorizationCodeFlow) object, cannot finish OAuth process'
            )
            return

        token = self.oauth.refreshToken()
        if not token:
            self.connected.emit(False)
            if self.oauth:
                self.oauth.replyHandler().close()
            self.logger.error(
                'Failed to connect reddit account: OAuth object has no refresh token',
                exc_info=True
            )
            return

        self.reddit_utils.save_token(token)
        if self.oauth:
            self.oauth.replyHandler().close()
        self.connected.emit(True)
        self.logger.info('Successfully connected to reddit account')
