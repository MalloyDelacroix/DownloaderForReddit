from PyQt5.QtWidgets import (QWidget, QTextBrowser, QFontComboBox, QComboBox, QLabel, QMenu, QHBoxLayout,
                             QWidgetAction)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor, QFont

from ...utils import injector


class PostTextBrowser(QTextBrowser):

    detach_signal = pyqtSignal()
    attach_signal = pyqtSignal()

    def __init__(self, parent=None, **kwargs):
        QTextBrowser.__init__(self, parent=parent)
        self.settings_manager = injector.get_settings_manager()
        self.stand_alone = kwargs.get('stand_alone', False)

        self.post_text_font_size = self.settings_manager.database_view_post_text_font_size
        self.post_text_font = QFont(self.settings_manager.database_view_post_text_font, self.post_text_font_size)
        self.setFont(self.post_text_font)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.context_menu)

    def context_menu(self):
        menu = QMenu()
        font_box = QFontComboBox()
        font_box.setCurrentFont(self.post_text_font)
        font_box.currentFontChanged.connect(lambda: self.set_post_text_font(font=font_box.currentFont()))
        font_box.currentFontChanged.connect(menu.close)
        font_box_label = QLabel('Font:')
        layout = QHBoxLayout()
        layout.addWidget(font_box_label)
        layout.addWidget(font_box)
        font_box_widget = QWidget(self)
        font_box_widget.setLayout(layout)
        font_box_item = QWidgetAction(self)
        font_box_item.setDefaultWidget(font_box_widget)

        font_size_box = QComboBox()
        font_size_box.addItems(str(x) for x in range(4, 30))
        font_size_box.setCurrentText(str(self.post_text_font_size))
        font_size_label = QLabel('Font Size:')
        size_layout = QHBoxLayout()
        size_layout.addWidget(font_size_label)
        size_layout.addWidget(font_size_box)
        font_size_widget = QWidget(self)
        font_size_widget.setLayout(size_layout)
        font_size_box.currentIndexChanged.connect(lambda:
                                                  self.set_post_text_font(size=int(font_size_box.currentText())))
        font_size_box.currentIndexChanged.connect(menu.close)
        font_size_item = QWidgetAction(self)
        font_size_item.setDefaultWidget(font_size_widget)

        menu.addAction(font_box_item)
        menu.addAction(font_size_item)
        menu.addSeparator()
        if not self.stand_alone:
            menu.addAction('Detach Text Box', lambda: self.detach_signal.emit())
        menu.exec_(QCursor.pos())

    def set_post_text_font(self, font=None, size=None):
        """
        Sets the font and size of the post text browser.
        :param font: The font that the post text browser should be set to display.
        :param size: The size of the font for the post text browser
        """
        if font is not None:
            self.post_text_font = font
            font.setPointSize(self.post_text_font_size)
            self.post_text_font = font
            self.setFont(font)
        if size is not None:
            self.post_text_font_size = size
            font = self.font()
            font.setPointSize(size)
            self.post_text_font = font
            self.setFont(font)

    def handle_dialog_movement(self):
        if self.stand_alone:
            self.attach_signal.emit()
        else:
            self.detach_signal.emit()

    def set_title(self, title):
        if self.stand_alone:
            self.parent().setWindowTitle(title)
