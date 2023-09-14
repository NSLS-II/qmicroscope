import time
from qtpy.QtCore import Signal, QPoint, QSize, Qt
from qtpy.QtGui import QBrush, QPainter, QPalette, QContextMenuEvent, QMouseEvent
from qtpy.QtWidgets import QWidget, QRubberBand, QSizeGrip, QHBoxLayout
from typing import List, Any, Dict, Optional, NamedTuple


class ResizableRubberBand(QWidget):
    box_modified = Signal(QPoint, QPoint)

    def __init__(
        self,
        parent: "QWidget|None" = None,
        draggable: bool = True,
        dragging_threshold: int = 1,
    ):
        super().__init__(parent)

        self.draggable: bool = draggable
        self.dragging_threshold: int = dragging_threshold
        self.mousePressPos: "QPoint|None" = None
        self.mouseMovePos: "QPoint|None" = None

        self.setWindowFlags(Qt.SubWindow)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QSizeGrip(self), 0, Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(QSizeGrip(self), 0, Qt.AlignRight | Qt.AlignBottom)
        self._band = QRubberBand(QRubberBand.Rectangle, self)
        self._band.setMaximumSize(
            QSize(self.parent().geometry().width(), self.parent().geometry().height())
        )
        palette = QPalette()
        palette.setBrush(QPalette.WindowText, QBrush(Qt.red))
        self._band.setPalette(palette)
        self._band.setWindowOpacity(0.0)
        self._band.show()
        self.show()

    def resizeEvent(self, a0):
        self._band.resize(self.size())
        self.box_modified.emit(self.geometry().topLeft(), self.geometry().bottomRight())

    def paintEvent(self, a0):
        # Get current window size
        qp = QPainter()
        qp.begin(self)
        self.update()
        qp.end()

    def mousePressEvent(self, a0: QMouseEvent):
        if self.draggable and a0.button() == Qt.RightButton:
            self.mousePressPos = a0.globalPos()  # global
            self.mouseMovePos = a0.globalPos() - self.pos()  # local

    def contextMenuEvent(self, a0: QContextMenuEvent) -> None:
        a0.accept()

    def mouseMoveEvent(self, a0: QMouseEvent):
        if self.draggable and a0.buttons() == Qt.RightButton:
            globalPos = a0.globalPos()
            moved: QPoint = globalPos - self.mousePressPos
            if moved.manhattanLength() > self.dragging_threshold:
                # Move when user drag window more than dragging_threshold
                diff: QPoint = globalPos - self.mouseMovePos
                self.move(diff)
                self.mouseMovePos = globalPos - self.pos()
                self.box_modified.emit(
                    self.geometry().topLeft(), self.geometry().bottomRight()
                )
        super().mouseMoveEvent(a0)

    def mouseReleaseEvent(self, a0: QMouseEvent):
        if self.mousePressPos is not None:
            if a0.button() == Qt.RightButton:
                moved: QPoint = a0.globalPos() - self.mousePressPos
                if moved.manhattanLength() > self.dragging_threshold:
                    # Do not call click event or so on
                    a0.ignore()
                self.mousePressPos = None

        super().mouseReleaseEvent(a0)

    def toggle_selector(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
