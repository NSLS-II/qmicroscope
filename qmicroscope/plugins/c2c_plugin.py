import typing

from qtpy.QtCore import QObject, QPoint, Qt, Signal
from qtpy.QtGui import QKeyEvent

from qmicroscope.plugins.base_plugin import BasePlugin

if typing.TYPE_CHECKING:
    from qmicroscope.microscope import Microscope


class ClickedSignal(QObject):
    clicked = Signal(object)


class C2CPlugin(BasePlugin):
    def __init__(self, parent: "Optional[Microscope]" = None):
        """Initializes the C2CPlugin instance.

        Args:
            parent (Optional[Microscope]): The microscope application that the plugin is attached to.
        """
        super().__init__(parent)
        self.name = "Click to center"
        self.parent = parent
        self.c2c_active = False
        self.clicked_signal = ClickedSignal()

    def mouse_press_event(self, event):
        if self.parent:
            self.parent: "Microscope"
            if self.c2c_active:
                delta_x = event.pos().x() - int(self.parent.view.width() / 2)
                delta_y = -(
                    event.pos().y() - int(self.parent.view.height() / 2)
                )  # Up is negative y and down is positive
                delta = QPoint(delta_x, delta_y)
                print(delta)
                self.clicked_signal.clicked.emit(delta)

    def key_press_event(self, event):
        if event.key() == Qt.Key.Key_Control:
            self.c2c_active = True
            self.parent.setCursor(Qt.CursorShape.CrossCursor)

    def key_release_event(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Control:
            self.c2c_active = False
            self.parent.unsetCursor()
