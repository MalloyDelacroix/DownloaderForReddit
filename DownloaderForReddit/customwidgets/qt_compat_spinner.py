"""
PyQt5 compatibility wrapper for pyqtspinner.WaitingSpinner.

pyqtspinner==0.1.1 passes float values to Qt methods that require int
(setFixedSize, setInterval, move) in PyQt5 >= 5.15.x. This subclass
overrides the three offending methods with explicit int casts so that
the rest of the codebase can import CompatibleWaitingSpinner as a
drop-in replacement without touching the installed library.

When pyqtspinner releases a fixed version, this file can be deleted and
all import sites reverted to `from pyqtspinner.spinner import WaitingSpinner`.
See: https://github.com/z3ntu/QtWaitingSpinner

"""

from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter

from pyqtspinner.spinner import WaitingSpinner


class CompatibleWaitingSpinner(WaitingSpinner):
    """WaitingSpinner with PyQt5 >= 5.15 int-argument compatibility fixes.

    pyqtspinner 0.1.1 passes float values to several Qt methods that now
    strictly require int in PyQt5 >= 5.15:
      - QRect() constructor arguments
      - QWidget.setFixedSize()
      - QTimer.setInterval()
      - QWidget.move()
    All fixes are isolated here so the installed library is never modified.
    """

    def paintEvent(self, event):
        # NOTE: This method is a full copy of WaitingSpinner.paintEvent with the
        # single change of casting QRect arguments to int (see drawRoundedRect
        # below). A targeted monkey-patch is not possible here because the fix
        # sits inside a loop within the parent method. If upstream pyqtspinner
        # adds features to paintEvent, this override must be updated accordingly.
        self.updatePosition()
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.transparent)
        painter.setRenderHint(QPainter.Antialiasing, True)

        if self._currentCounter >= self._numberOfLines:
            self._currentCounter = 0

        painter.setPen(Qt.NoPen)
        for i in range(self._numberOfLines):
            painter.save()
            painter.translate(self._innerRadius + self._lineLength,
                              self._innerRadius + self._lineLength)
            rotate_angle = float(360 * i) / float(self._numberOfLines)
            painter.rotate(rotate_angle)
            painter.translate(self._innerRadius, 0)
            distance = self.lineCountDistanceFromPrimary(
                i, self._currentCounter, self._numberOfLines)
            color = self.currentLineColor(
                distance, self._numberOfLines, self._trailFadePercentage,
                self._minimumTrailOpacity, self._color)
            painter.setBrush(color)
            painter.drawRoundedRect(
                # int() truncates toward zero: for lineWidth=5, -5/2=-2.5 → -2.
                # Sub-pixel difference is imperceptible for a spinner widget.
                QRect(0,
                      int(-self._lineWidth / 2),
                      int(self._lineLength),
                      int(self._lineWidth)),
                self._roundness,
                self._roundness,
                Qt.RelativeSize,
            )
            painter.restore()

    def updateSize(self):
        # QWidget.setFixedSize requires int arguments.
        size = int((self._innerRadius + self._lineLength) * 2)
        self.setFixedSize(size, size)

    def updateTimer(self):
        # QTimer.setInterval requires an int (milliseconds).
        interval = int(1000 / (self._numberOfLines * self._revolutionsPerSecond))
        self._timer.setInterval(interval)

    def updatePosition(self):
        # QWidget.move requires int arguments.
        if self.parentWidget() and self._centerOnParent:
            x = (self.parentWidget().width() - self.width()) // 2
            y = (self.parentWidget().height() - self.height()) // 2
            self.move(x, y)
