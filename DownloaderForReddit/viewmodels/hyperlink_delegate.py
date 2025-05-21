from PyQt5.QtWidgets import QStyledItemDelegate
from PyQt5.QtGui import QTextDocument
from PyQt5.QtCore import QEvent, Qt
import webbrowser


class HyperlinkDelegate(QStyledItemDelegate):
    """
    Provides a delegate for rendering hyperlinks in item views.

    This class inherits from QStyledItemDelegate and is used to display and interact with
    content containing hyperlinks within item views. It renders HTML content and handles
    mouse events to support hyperlink navigation.
    """
    def paint(self, painter, option, index):
        doc = QTextDocument()
        doc.setHtml(index.data(Qt.DisplayRole))
        doc.setTextWidth(option.rect.width())
        painter.save()
        painter.translate(option.rect.topLeft())
        doc.drawContents(painter)
        painter.restore()

    def sizeHint(self, option, index):
        doc = QTextDocument()
        doc.setHtml(index.data(Qt.DisplayRole))
        doc.setTextWidth(option.rect.width())
        return doc.size().toSize()

    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            doc = QTextDocument()
            doc.setHtml(index.data(Qt.DisplayRole))
            pos = event.pos() - option.rect.topLeft()
            anchor = doc.documentLayout().anchorAt(pos)
            if anchor:
                webbrowser.open(anchor)
                return True
        return False
