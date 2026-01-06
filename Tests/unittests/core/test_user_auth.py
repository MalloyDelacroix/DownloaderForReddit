from unittest import TestCase
from unittest.mock import MagicMock, patch
from PyQt5.QtCore import QByteArray, QUrl
from PyQt5.QtNetwork import QNetworkRequest
from DownloaderForReddit.core.user_auth import UaNetworkAccessManager, UserAuth

class TestUaNetworkAccessManager(TestCase):

    def test_create_request_sets_user_agent(self):
        user_agent = "TestAgent"
        manager = UaNetworkAccessManager(user_agent)
        
        request = QNetworkRequest(QUrl("http://example.com"))
        
        with patch.object(QNetworkRequest, 'setRawHeader') as mock_set_header:
            manager.createRequest(manager.GetOperation, request)
            mock_set_header.assert_any_call(QByteArray(b'User-Agent'), QByteArray(user_agent.encode('utf-8')))

class TestUserAuth(TestCase):

    def setUp(self):
        self.mock_reddit_utils = MagicMock()
        self.mock_reddit_utils.CLIENT_ID = "test_client_id"
        self.mock_reddit_utils.USER_AGENT = "test_user_agent"
        self.mock_reddit_utils.REDIRECT_URL = "http://localhost:8086"
        self.mock_reddit_utils.TOKEN_SCOPES = ["identity", "read"]
        
        self.user_auth = UserAuth(self.mock_reddit_utils)

    def test_init(self):
        self.assertEqual(self.user_auth.client_id, "test_client_id")
        self.assertEqual(self.user_auth.user_agent, "test_user_agent")
        self.assertEqual(self.user_auth.redirect_uri, "http://localhost:8086")
        self.assertEqual(self.user_auth.token_scope, ["identity", "read"])
        self.assertEqual(self.user_auth.authorization_url, QUrl("https://www.reddit.com/api/v1/authorize"))
        self.assertEqual(self.user_auth.access_url, QUrl("https://www.reddit.com/api/v1/access_token"))
        self.assertIsNone(self.user_auth.oauth)

    @patch('DownloaderForReddit.core.user_auth.QDesktopServices')
    @patch('DownloaderForReddit.core.user_auth.QOAuth2AuthorizationCodeFlow')
    @patch('DownloaderForReddit.core.user_auth.QOAuthHttpServerReplyHandler')
    @patch('DownloaderForReddit.core.user_auth.UaNetworkAccessManager')
    def test_start_oauth(self, mock_ua_manager, mock_reply_handler, mock_oauth_flow, mock_desktop_services):
        mock_oauth_instance = mock_oauth_flow.return_value
        
        oauth = self.user_auth.start_oauth()
        
        self.assertEqual(oauth, mock_oauth_instance)
        mock_ua_manager.assert_called_once_with(self.user_auth.user_agent, self.user_auth)
        mock_reply_handler.assert_called_once_with(8086)
        
        mock_oauth_flow.assert_called_once()
        mock_oauth_instance.granted.connect.assert_called_with(self.user_auth.finish_oauth)
        mock_oauth_instance.error.connect.assert_called()
        mock_oauth_instance.authorizeWithBrowser.connect.assert_called_with(mock_desktop_services.openUrl)
        mock_oauth_instance.setReplyHandler.assert_called_once_with(mock_reply_handler.return_value)
        mock_oauth_instance.setScope.assert_called_once_with("identity read")
        mock_oauth_instance.setUserAgent.assert_called_once_with(self.user_auth.user_agent)
        
        mock_oauth_instance.resourceOwnerAuthorization.assert_called_once()

    def test_finish_oauth_success(self):
        self.user_auth.oauth = MagicMock()
        self.user_auth.oauth.refreshToken.return_value = "test_refresh_token"
        
        mock_slot = MagicMock()
        self.user_auth.connected.connect(mock_slot)
        
        self.user_auth.finish_oauth()
        
        self.mock_reddit_utils.save_token.assert_called_once_with("test_refresh_token")
        self.user_auth.oauth.replyHandler().close.assert_called_once()
        mock_slot.assert_called_once_with(True)

    def test_finish_oauth_failure(self):
        self.user_auth.oauth = MagicMock()
        self.user_auth.oauth.refreshToken.return_value = None
        
        mock_slot = MagicMock()
        self.user_auth.connected.connect(mock_slot)
        
        self.user_auth.finish_oauth()
        
        self.mock_reddit_utils.save_token.assert_not_called()
        self.user_auth.oauth.replyHandler().close.assert_called_once()
        mock_slot.assert_called_once_with(False)

    def test_finish_oauth_no_oauth_instance(self):
        self.user_auth.oauth = None
        
        mock_slot = MagicMock()
        self.user_auth.connected.connect(mock_slot)
        
        with patch.object(self.user_auth.logger, 'error') as mock_log_error:
            self.user_auth.finish_oauth()
            
            mock_slot.assert_called_once_with(False)
            mock_log_error.assert_called_once_with(
                'Failed to create OAuth (QOAuth2AuthorizationCodeFlow) object, cannot finish OAuth process'
            )

    @patch('DownloaderForReddit.core.user_auth.QOAuth2AuthorizationCodeFlow')
    def test_start_oauth_error_logging(self, mock_oauth_flow):
        # Test if error signal is connected to logger
        mock_oauth_instance = mock_oauth_flow.return_value
        with patch.object(self.user_auth.logger, 'error') as mock_log_error:
            self.user_auth.start_oauth()
            
            # Get the lambda connected to error
            error_callback = None
            for call in mock_oauth_instance.error.connect.call_args_list:
                args, _ = call
                if callable(args[0]):
                    error_callback = args[0]
            
            self.assertIsNotNone(error_callback)
            error_callback("error_code", "error_description")
            mock_log_error.assert_called_once_with('OAuth error: error_code - error_description')

    def test_finish_oauth_no_oauth_instance_at_cleanup(self):
        # This tests the 'if self.oauth' check in finish_oauth during failure cleanup
        self.user_auth.oauth = MagicMock()
        self.user_auth.oauth.refreshToken.return_value = None
        
        # We want to see what happens if self.oauth becomes None AFTER refreshToken call but BEFORE close call
        # though it's unlikely in single thread, we can mock it by making refreshToken side effect
        def side_effect():
            self.user_auth.oauth = None
            return None
        
        self.user_auth.oauth.refreshToken.side_effect = side_effect
        
        mock_slot = MagicMock()
        self.user_auth.connected.connect(mock_slot)
        
        self.user_auth.finish_oauth()
        mock_slot.assert_called_once_with(False)
