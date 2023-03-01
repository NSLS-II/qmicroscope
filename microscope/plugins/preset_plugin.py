from typing import Optional, Dict, Any, TYPE_CHECKING
from qtpy.QtWidgets import QAction, QMenu, QInputDialog
from microscope.plugins.base_plugin import BasePlugin
from qtpy.QtGui import QMouseEvent

if TYPE_CHECKING:
    from microscope.microscope import Microscope


class PresetPlugin(BasePlugin):
    """Plugin to save the state of plugins into the settings file and give it a name"""

    def __init__(self, parent: "Optional[Microscope]" = None):
        super().__init__(parent)
        self.parent = parent
        self.name = "Camera Presets"
        self.presets: Dict[str, Any] = {}
        self.preset_actions = {}
        self.selected_preset = None

    def context_menu_entry(self):
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

    def start_plugin(self):
        pass

    def stop_plugin(self):
        pass

    def read_settings(self, settings: Dict[str, Any]):
        self.presets = settings

    def write_settings(self) -> Dict[str, Any]:
        return self.presets

    def _save_preset(self):
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
        if self.selected_preset:
            self.preset_actions[self.selected_preset].setChecked(False)
        preset_values = self.presets[preset_name]
        self.selected_preset = preset_name
        for plugin in self.parent.plugins:
            if plugin != self and plugin.name in preset_values:
                plugin.read_settings(preset_values[plugin.name])

    def mouse_move_event(self, event: QMouseEvent):
        pass

    def mouse_press_event(self, event: QMouseEvent):
        pass

    def mouse_release_event(self, event: QMouseEvent):
        pass
