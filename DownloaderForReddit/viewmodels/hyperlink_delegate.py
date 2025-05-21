from PyQt5.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem
from PyQt5.QtGui import QTextDocument, QTextCursor, QTextCharFormat
from PyQt5.QtCore import QEvent, Qt, QModelIndex
import webbrowser


class HyperlinkDelegate(QStyledItemDelegate):
    """
    Provides a delegate for rendering hyperlinks in item views.

    This class inherits from QStyledItemDelegate and is used to display and interact with
    content containing hyperlinks within item views. It renders HTML content and handles
    mouse events to support hyperlink navigation while preserving the item's intended
    color.
    """
    def paint(self, painter, option, index):
        """
        Overrides the paint method to render hyperlinks and colored text in the item view.

        :param painter: QPainter object used for rendering the text.
        :param option: QStyleOptionViewItem containing options for rendering the item.
        :param index: QModelIndex providing access to model data.
        :return: None
        """
        doc = self.get_document(option, index)

        painter.save()
        painter.translate(option.rect.topLeft())
        doc.drawContents(painter)
        painter.restore()

    def sizeHint(self, option, index):
        """
        Overrides the sizeHint method to return the size of the document element after
        the formatting is applied to render the HTML correctly.

        :param option: Contains style option controls for rendering items
        :param index: Refers to the model index of the item
        :return: Calculated size of the item as a QSize object
        """
        doc = self.get_document(option, index)
        return doc.size().toSize()

    def get_document(self, option: QStyleOptionViewItem, index: QModelIndex) -> QTextDocument:
        """
        Generates a QTextDocument object with formatted HTML content and foreground
        color based on provided index data. The method applies formatting to the
        HTML content before setting it to the document and adjusts the text width
        according to the specified option.

        :param option: The style option which provides information such as the rectangle
                       dimensions to adjust the document's text width.
        :param index: The model index containing data for the document, such as HTML content
                      and optional foreground color.
        :return: A QTextDocument object set with the formatted HTML content and modified
                 foreground color (if applicable).
        """
        doc = QTextDocument()
        html = index.data(Qt.DisplayRole)
        formatted_html = self.format_html(html)
        doc.setHtml(formatted_html)
        color = index.data(Qt.ForegroundRole)

        if color:
            cursor = QTextCursor(doc)
            cursor.select(QTextCursor.Document)
            fmt = QTextCharFormat()
            fmt.setForeground(color)
            cursor.mergeCharFormat(fmt)

        doc.setTextWidth(option.rect.width())
        return doc

    def editorEvent(self, event, model, option, index):
        """
        Overrides the editorEvent method to handle mouse events for hyperlink navigation.
        """
        if event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            doc = QTextDocument()
            doc.setHtml(index.data(Qt.DisplayRole))
            pos = event.pos() - option.rect.topLeft()
            anchor = doc.documentLayout().anchorAt(pos)
            if anchor:
                webbrowser.open(anchor)
                return True
        return False

    @staticmethod
    def format_html(html_text: str) -> str:
        """
        Formats a given HTML text by replacing newline characters with HTML line break
        tags and wrapping the entire text with paragraph tags.

        :param html_text: The HTML text to format.
        :return: The formatted HTML text.
        """
        html_text = html_text.replace('\n', '<br/>')
        return f'<p>{html_text}</p>'
