from PyQt5.QtWidgets import QWizard

from ..guiresources.user_auth_wizard_auto import Ui_UserAuthWizard
from ..utils import reddit_utils


class UserAuthWizard(QWizard, Ui_UserAuthWizard):

    def __init__(self, parent=None):
        QWizard.__init__(self, parent=parent)
        self.setupUi(self)
        self.authorize_account_url_label.setVisible(False)
        self.load_url()
        self.button(QWizard.NextButton).clicked.connect(self.handle_next_click)

    def load_url(self):
        url = reddit_utils.get_authorize_account_url()
        print(url)
        url_text = f'<a href="{url}">{url}</a>'
        self.authorize_account_url_label.setText(url_text)
        self.authorize_account_url_label.setVisible(True)

    def handle_next_click(self):
        if self.currentPage().isFinalPage():
            self.connect_reddit_account()

    def connect_reddit_account(self):
        url = self.auth_url_line_edit.text()
        if url is not None and url != '' and url != ' ':
            user = reddit_utils.get_user_authorization_token(url)
            if user is not None:
                self.user_name_verification_label.setText(user.name)
            else:
                self.user_name_verification_label.setText(
                    'An error occurred and your reddit account could not be linked.  Please try again.'
                )
