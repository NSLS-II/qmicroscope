from typing import Dict, Any, Optional, List
from qtpy.QtGui import QMouseEvent, QImage
from qtpy.QtWidgets import QGroupBox, QAction


class BasePlugin:
    def __init__(self, parent) -> None:
        self.name = "Generic Plugin"
        self.updates_image = False
        self.parent = parent

    def context_menu_entry(self) -> List[QAction]:
        return []

    def update_image_data(self, image: QImage):
        return image

    def mouse_press_event(self, event: QMouseEvent):
        pass

    def mouse_move_event(self, event: QMouseEvent):
        pass

    def mouse_release_event(self, event: QMouseEvent):
        pass

    def read_settings(self, settings: Dict[str, Any]):
        pass

    def write_settings(self) -> Dict[str, Any]:
        return {}

    def start_plugin(self):
        pass

    def stop_plugin(self):
        pass

    def add_settings(self, parent=None) -> Optional[QGroupBox]:
        return None

    def save_settings(self, settings_groupbox) -> None:
        pass


class BaseImagePlugin(BasePlugin):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.name = "Base Image Plugin"
        self.updates_image = True
