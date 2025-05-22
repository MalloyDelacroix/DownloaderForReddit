from PyQt5.QtCore import QEvent, Qt, QObject
from PyQt5.QtGui import QTextDocument


class LinkCursorHandler(QObject):
    """
    Handles mouse cursor changes when hovering over items that contain links in a
    list view.

    This class monitors mouse movements and dynamically changes the cursor to
    indicate actionable links within items in a list view. This is achieved by
    installing an event filter on the viewport of the list view. It detects mouse
    hovering on HTML elements within the list view and updates the cursor
    to a pointer when hovering over hyperlinks.  The cursor is otherwise
    reset to a default cursor.

    :ivar view: The associated list view widget whose mouse events are being tracked.
    :type view: QListView
    """
    def __init__(self, list_view):
        super().__init__()
        self.view = list_view
        self.view.setMouseTracking(True)
        self.view.viewport().installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseMove:
            index = self.view.indexAt(event.pos())
            if not index.isValid():
                self.view.setCursor(Qt.ArrowCursor)
                return False

            option = self.view.viewOptions()
            option.rect = self.view.visualRect(index)

            html = index.data(Qt.DisplayRole)
            doc = QTextDocument()
            doc.setHtml(html)
            pos_in_item = event.pos() - option.rect.topLeft()

            anchor = doc.documentLayout().anchorAt(pos_in_item)
            if anchor:
                self.view.setCursor(Qt.PointingHandCursor)
            else:
                self.view.setCursor(Qt.ArrowCursor)

        elif event.type() == QEvent.Leave:
            self.view.setCursor(Qt.ArrowCursor)

        return False
