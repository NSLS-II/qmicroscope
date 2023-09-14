from typing import Optional, Dict, Any, TYPE_CHECKING
from qtpy.QtWidgets import QAction, QMenu, QInputDialog
from qmicroscope.plugins.base_plugin import BasePlugin
from qtpy.QtGui import QMouseEvent

if TYPE_CHECKING:
    from qmicroscope.microscope import Microscope


class PresetPlugin(BasePlugin):
    """
    A plugin that allows the user to save and load presets of other plugins' settings.

    Attributes:
        parent (Optional[Microscope]): The parent Microscope instance.
        name (str): The name of this plugin.
        presets (Dict[str, Any]): A dictionary of saved presets, where the keys are preset names and the values
            are dictionaries of plugin settings.
        preset_actions (dict): A dictionary of QAction instances representing the presets.
        selected_preset (str): The name of the currently selected preset, or None if no preset is selected.
    """

    def __init__(self, parent: "Optional[Microscope]" = None):
        """
        Initializes a new instance of the PresetPlugin class.

        Args:
            parent (Optional[Microscope]): The parent Microscope instance.
        """
        super().__init__(parent)
        self.parent = parent
        self.name = "Camera Presets"
        self.presets: Dict[str, Any] = {}
        self.preset_actions = {}
        self.selected_preset = None

    def context_menu_entry(self):
        """
        Creates a context menu entry for this plugin.

        Returns:
            List[QAction]: A list of QAction instances for the context menu entry.
        """
        actions = []
        self.save_preset_action = QAction("Save Preset", self.parent)
        self.save_preset_action.triggered.connect(self._save_preset)
        actions.append(self.save_preset_action)

        preset_menu = QMenu(title="Presets", parent=self.parent)
        if self.presets:
            for preset in self.presets.keys():
                if preset not in self.preset_actions:
                    checked = True if preset == self.selected_preset else False
                    self.preset_actions[preset] = QAction(
                        preset, self.parent, checkable=True, checked=checked
                    )
                    self.preset_actions[preset].triggered.connect(
                        lambda val, preset=preset: self._load_preset(preset)
                    )
            preset_menu.addActions(list(self.preset_actions.values()))
        actions.append(preset_menu)

        return actions

    def read_settings(self, settings: Dict[str, Any]):
        """
        Reads the plugin settings from a dictionary.

        Args:
            settings (Dict[str, Any]): A dictionary containing the plugin settings.
        """
        self.presets = settings

    def write_settings(self) -> Dict[str, Any]:
        """
        Writes the plugin settings to a dictionary.

        Returns:
            Dict[str, Any]: A dictionary containing the plugin settings.
        """
        return self.presets

    def _save_preset(self):
        """
        Saves a preset of the current plugin settings.
        """
        preset_name, ok = QInputDialog.getText(
            self.parent, "Preset name", "Enter preset name"
        )
        if ok:
            preset_values = {}
            for plugin in self.parent.plugins:
                if plugin != self:
                    preset_values[plugin.name] = plugin.write_settings()
            self.presets[preset_name] = preset_values
            self.parent.writeSettings()

    def _load_preset(self, preset_name):
        """
        Loads a preset of plugin settings.

        Args:
            preset_name (str): The name of the preset to load.
        """
        if self.selected_preset:
            self.preset_actions[self.selected_preset].setChecked(False)
        preset_values = self.presets[preset_name]
        self.selected_preset = preset_name
        for plugin in self.parent.plugins:
            if plugin != self and plugin.name in preset_values:
                plugin.read_settings(preset_values[plugin.name])
