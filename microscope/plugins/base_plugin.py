from typing import Dict, Any, Optional, List
from qtpy.QtGui import QMouseEvent, QImage
from qtpy.QtWidgets import QGroupBox, QAction


class BasePlugin:
    def __init__(self, parent) -> None:
        self.name = "Generic Plugin"
        self.updates_image = False
        self.parent = parent

    def context_menu_entry(self) -> List[QAction]:
        """
        Add actions into the (right-click) context menu. The microscope widget will call this function when the
        user right clicks the widget

        Returns:
            List of QActions
        """
        return []

    def update_image_data(self, image: QImage) -> QImage:
        """
        Manipulates or uses image data provided by the microscope widget. Will only be
        called if self.updates_image is set to True

        Args:
            image: QImage instance
        returns:
            QImage instance
        """
        return image

    def mouse_press_event(self, event: QMouseEvent):
        pass

    def mouse_move_event(self, event: QMouseEvent):
        pass

    def mouse_release_event(self, event: QMouseEvent):
        pass

    def read_settings(self, settings: Dict[str, Any]):
        """
        Receives a dictionary of settings from the microscope widget.
        This data should be used to set up the plugin.
        Note: It is up to the plugin author to convert dictionary values to its appropriate type
        In Linux systems everything is stored as a string (for e.g. boolean values are 'true' and 'false' strings)

        Argument:
            settings: Dictionary of setting values
        """
        pass

    def write_settings(self) -> Dict[str, Any]:
        """
        Provide a dictionary of settings to the caller. Usually to save it to disk. The dictionary
        returned here is what is passed as an argument when read_settings is called.

        Returns:
            Dictionary of settings
        """
        return {}

    def start_plugin(self):
        """
        Hook to set up the plugin after the microscope starts acquiring image data. For example,
        if we don't know the image size when the plugin is initialized, we can look for it here.
        Or draw something after the image is shown
        """
        pass

    def stop_plugin(self):
        """
        Hook to do something just before acquiring stops. For example, remove a drawing
        """
        pass

    def add_settings(self, parent=None) -> Optional[QGroupBox]:
        """
        Returns an optional QGroupBox that is displayed in the "Configure plugins" window

        returns:
            Optional QGroupBox
        """
        return None

    def save_settings(self, settings_groupbox) -> None:
        """
        This function is called when the user clicks on Ok or Apply in the "configure plugins" window
        """
        pass


class BaseImagePlugin(BasePlugin):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.name = "Base Image Plugin"
        self.updates_image = True
