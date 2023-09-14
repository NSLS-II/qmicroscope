import pytest
from qtpy.QtWidgets import (
    QDialog,
    QPushButton,
    QGroupBox,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QSpacerItem,
    QWidgetItem,
)
from qtpy import QtCore
from qmicroscope.plugin_settings import PluginSettingsDialog, BasePlugin


@pytest.fixture
def plugin_settings_dialog(qtbot):
    """
    Creates an instance of PluginSettingsDialog for testing purposes.
    """
    plugins = [BasePlugin(qtbot), BasePlugin(qtbot), BasePlugin(qtbot)]
    plugin_settings_dialog = PluginSettingsDialog(plugins=plugins)
    qtbot.addWidget(plugin_settings_dialog)
    return plugin_settings_dialog


def test_plugin_settings_dialog_creation(plugin_settings_dialog):
    """
    Test that PluginSettingsDialog is created successfully.
    """
    assert isinstance(plugin_settings_dialog, QDialog)


def test_plugin_settings_dialog_title(plugin_settings_dialog):
    """
    Test that PluginSettingsDialog has the correct title.
    """
    assert plugin_settings_dialog.windowTitle() == "Plugin Configuration"


def test_plugin_settings_dialog_buttons(plugin_settings_dialog):
    """
    Test that PluginSettingsDialog has the correct buttons.
    """
    assert isinstance(plugin_settings_dialog.okButton, QPushButton)
    assert isinstance(plugin_settings_dialog.applyButton, QPushButton)
    assert isinstance(plugin_settings_dialog.cancelButton, QPushButton)
    assert plugin_settings_dialog.okButton.text() == "OK"
    assert plugin_settings_dialog.applyButton.text() == "Apply"
    assert plugin_settings_dialog.cancelButton.text() == "Cancel"


def test_plugin_settings_dialog_groupboxes(plugin_settings_dialog):
    """
    Test that PluginSettingsDialog has the correct group boxes.
    """
    assert isinstance(plugin_settings_dialog.plugin_groupboxes, dict)
    assert len(plugin_settings_dialog.plugin_groupboxes) == 3
    for plugin, groupbox in plugin_settings_dialog.plugin_groupboxes.items():
        assert isinstance(plugin, BasePlugin)
        assert isinstance(groupbox, (QGroupBox, type(None)))


def test_plugin_settings_dialog_layout(plugin_settings_dialog):
    """
    Test that PluginSettingsDialog has the correct layout.
    """
    assert isinstance(plugin_settings_dialog.layout(), QVBoxLayout)
    assert isinstance(plugin_settings_dialog.layout().itemAt(0), QFormLayout)
    assert isinstance(plugin_settings_dialog.layout().itemAt(1), QHBoxLayout)
    assert isinstance(plugin_settings_dialog.layout().itemAt(1).itemAt(0), QSpacerItem)
    assert isinstance(plugin_settings_dialog.layout().itemAt(1).itemAt(1), QWidgetItem)
    assert isinstance(plugin_settings_dialog.layout().itemAt(1).itemAt(2), QWidgetItem)
    assert isinstance(plugin_settings_dialog.layout().itemAt(1).itemAt(3), QWidgetItem)


def test_plugin_settings_dialog_ok_clicked(qtbot, plugin_settings_dialog):
    """
    Test that PluginSettingsDialog's OK button works correctly.
    """
    qtbot.mouseClick(plugin_settings_dialog.okButton, QtCore.Qt.LeftButton)
    for plugin, groupbox in plugin_settings_dialog.plugin_groupboxes.items():
        if groupbox:
            assert plugin.settings_saved == True
    assert plugin_settings_dialog.result() == QDialog.Accepted


def test_plugin_settings_dialog_apply_clicked(qtbot, plugin_settings_dialog):
    """
    Test that PluginSettingsDialog's Apply button works correctly.
    """
    qtbot.mouseClick(plugin_settings_dialog.applyButton, QtCore.Qt.LeftButton)
    for plugin, groupbox in plugin_settings_dialog.plugin_groupboxes.items():
        if groupbox:
            assert plugin.settings_saved == True


def test_plugin_settings_dialog_cancel_clicked(qtbot, plugin_settings_dialog: QDialog):
    """
    Test that PluginSettingsDialog's Cancel button works correctly.
    """
    qtbot.mouseClick(plugin_settings_dialog.cancelButton, QtCore.Qt.LeftButton)
    assert plugin_settings_dialog.close() == True
