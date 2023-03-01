from qtpy.QtCore import Signal
from qtpy.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QGroupBox,
)
from typing import Dict, Optional
from microscope.plugins.base_plugin import BasePlugin


class PluginSettingsDialog(QDialog):
    def __init__(self, parent=None, plugins=None) -> None:
        super().__init__(parent)
        if plugins:
            self.plugins = plugins
        else:
            self.plugins = []

        self.plugin_groupboxes: Dict[BasePlugin, Optional[QGroupBox]] = {}
        for plugin in self.plugins:
            self.plugin_groupboxes[plugin] = plugin.add_settings(parent=self)

        self.setModal(True)

        self.okButton = QPushButton("OK")
        self.applyButton = QPushButton("Apply")
        self.cancelButton = QPushButton("Cancel")

        self.okButton.clicked.connect(self.okClicked)
        self.applyButton.clicked.connect(self.applyClicked)
        self.cancelButton.clicked.connect(self.cancelClicked)

        self.setWindowTitle("Plugin Configuration")
        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(self.okButton)
        hbox.addWidget(self.applyButton)
        hbox.addWidget(self.cancelButton)
        hbox.addStretch()
        vbox = QVBoxLayout()
        formLayout = self.generate_layout()
        vbox.addLayout(formLayout)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

        self.show()

    def generate_layout(self):
        layout = QFormLayout()
        for plugin, widget in self.plugin_groupboxes.items():
            if widget:
                layout.addWidget(widget)

        return layout

    def okClicked(self):
        self.applyClicked()
        self.accept()

    def applyClicked(self):
        for plugin, widget in self.plugin_groupboxes.items():
            if widget:
                plugin.save_settings(widget)

    def cancelClicked(self):
        self.reject()
