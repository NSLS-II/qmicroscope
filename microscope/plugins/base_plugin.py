from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from qtpy.QtGui import QMouseEvent, QImage
from qtpy.QtCore import QSettings
from qtpy.QtWidgets import QWidget, QGroupBox

class BasePlugin(ABC):

    def __init__(self, parent) -> None:
        self.name = 'Generic Plugin'
        self.updates_image = False
        self.parent = parent
    
    @abstractmethod
    def context_menu_entry(self):
        pass

    def update_image_data(self, image: QImage):
        return image

    @abstractmethod
    def mouse_press_event(self, event: QMouseEvent):
        pass

    @abstractmethod
    def mouse_move_event(self, event: QMouseEvent):
        pass

    @abstractmethod
    def mouse_release_event(self, event: QMouseEvent):
        pass

    @abstractmethod
    def read_settings(self, settings: Dict[str, Any]):
        pass

    @abstractmethod
    def write_settings(self) -> Dict[str, Any]:
        pass


    def add_settings(self, parent=None) -> Optional[QGroupBox]:
        return None

    def save_settings(self, settings_groupbox) -> None:
        pass

class BaseImagePlugin(BasePlugin):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.name = 'Base Image Plugin'
        self.updates_image = True