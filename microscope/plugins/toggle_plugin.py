from typing import Optional, Dict, Any, TYPE_CHECKING
from qtpy.QtWidgets import QCheckBox
from microscope.plugins.base_plugin import BasePlugin
from qtpy.QtGui import QMouseEvent

if TYPE_CHECKING:
    from microscope.microscope import Microscope


class TogglePlugin(BasePlugin):
    def __init__(self, parent: "Microscope") -> None:
        """Initializes a TogglePlugin instance.

        Args:
            parent: The microscope instance to which this plugin is attached.
        """
        super().__init__(parent)
        self.parent = parent
        self.name = "Toggle Plugin"
        self.checkBox = QCheckBox(self.parent)
        self.checkBox.toggle()
        self.checkBoxProxy = self.parent.scene.addWidget(self.checkBox)
        # self.checkBoxProxy.setPos(100,100)
        self.checkBoxProxy.setZValue(1)
        self.checkBox.stateChanged.connect(self._toggle_cam)

    def _toggle_cam(self, state: bool):
        """Toggle the camera on or off"""
        self.parent.acquire(state)

    def context_menu_entry(self):
        return []

    def write_settings(self) -> Dict[str, Any]:
        return {}
