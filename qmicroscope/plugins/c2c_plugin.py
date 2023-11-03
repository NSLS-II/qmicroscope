import typing
from qtpy.QtCore import QObject, Signal
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
                delta = event.pos() - self.parent.center 
                print(delta)
                self.clicked_signal.clicked.emit(delta)

    def key_press_event(self, event):
        print(event)