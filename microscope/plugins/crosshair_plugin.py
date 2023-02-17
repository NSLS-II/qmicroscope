from microscope.plugins.base_plugin import BaseImagePlugin
from qtpy.QtGui import QColor, QPen, QMouseEvent
from qtpy.QtCore import QPoint, QLineF
from qtpy.QtWidgets import (QGraphicsScene, QAction, QColorDialog, 
                            QGroupBox, QFormLayout, QSpinBox,
                            QCheckBox, QHBoxLayout)
from typing import Dict, Any, Optional, TYPE_CHECKING
from microscope.widgets.color_button import ColorButton
if TYPE_CHECKING:
    from microscope.microscope import Microscope

class CrossHairPlugin(BaseImagePlugin):
    def __init__(self, parent: "Microscope") -> None:
        super().__init__(parent)
        self.name = 'Crosshair'
        self._color = QColor.fromRgb(0, 255, 0)
        self._pos = QPoint(int(parent.view.width()/2), 
                           int(parent.view.height()/2))
        self._always_centered = True
        self._horizontal_length = 100
        self._vertical_length = 100
        self._visible = True
        self._hor_line = None
        self._vert_line = None

    def read_settings(self, settings: Dict[str, Any]):
        self._color = settings.get('color', self._color)
        self._pos = settings.get('pos', self._pos)
        self._horizontal_length = int(settings.get('hor_len', self._horizontal_length))
        self._vertical_length = int(settings.get('vert_len', self._vertical_length))
        self._visible = settings.get('visible', self._visible)
        if isinstance(self._visible, str):
            self._visible = True if self._visible.lower() == 'true' else False
        self._always_centered = settings.get('always_centered', True)
        if isinstance(self._always_centered, str):
            self._always_centered = True if self._always_centered.lower() == 'true' else False
        self._paint_crosshair(self.parent.scene)

    def update_image_data(self, image):
        if self._always_centered:
            pos = QPoint(int(self.parent.view.width()/2), 
                           int(self.parent.view.height()/2))
            if pos != self._pos:
                self._paint_crosshair(self.parent.scene)

        return image

    def _paint_crosshair(self, scene: QGraphicsScene):
        if self._hor_line:
            scene.removeItem(self._hor_line)
        if self._vert_line:
            scene.removeItem(self._vert_line)

        pen = QPen(self._color)
        if self._always_centered:
            self._pos = QPoint(int(self.parent.view.width()/2), 
                           int(self.parent.view.height()/2)) 

        start_point = self._pos - QPoint(int(self._horizontal_length/2),0)
        end_point = self._pos + QPoint(int(self._horizontal_length/2),0) 
        hor_line = QLineF(start_point, end_point)
        self._hor_line = scene.addLine(hor_line, pen)

        start_point = self._pos + QPoint(0, int(self._vertical_length/2))
        end_point = self._pos - QPoint(0, int(self._vertical_length/2))
        vert_line = QLineF(start_point, end_point)
        self._vert_line = scene.addLine(vert_line, pen)

        self._toggle_visibility(self._visible)


    

    def context_menu_entry(self):
        actions = []
        #change_color_action = QAction('Change Color', self.parent)
        #change_color_action.triggered.connect(self._change_color)
        #actions.append(change_color_action)
        print(self._visible)
        visible_action = QAction('Visible', self.parent, checkable=True, checked=self._visible)
        visible_action.triggered.connect(self._toggle_visibility)
        actions.append(visible_action)
        return actions

    def _toggle_visibility(self, value):
        #self._visible = not self._visible
        self._visible = value
        self._hor_line.setVisible(self._visible)
        self._vert_line.setVisible(self._visible)

    def _change_color(self):
        self._color = QColorDialog.getColor()
        self._paint_crosshair(self.parent.scene)

    def mouse_press_event(self, event: QMouseEvent):
        pass

    def mouse_move_event(self, event: QMouseEvent):
        pass

    def mouse_release_event(self, event: QMouseEvent):
        pass

    def write_settings(self) -> Dict[str, Any]:
        settings = {}
        settings['color'] = self._color
        settings['pos'] = self._pos
        settings['hor_len'] = self._horizontal_length
        settings['vert_len'] = self._vertical_length
        settings['visible'] = self._visible
        settings['always_centered'] = self._always_centered

        return settings

    def add_settings(self, parent=None) -> Optional[QGroupBox]:
        parent = parent if parent else self.parent
        groupBox = QGroupBox(self.name, parent)
        layout = QFormLayout()
        self.color_setting_widget = ColorButton(parent=parent, color=self._color) 
        layout.addRow('Color', self.color_setting_widget)
        self.hor_len_setting_widget = QSpinBox()
        self.hor_len_setting_widget.setRange(1, 1000)
        self.hor_len_setting_widget.setValue(self._horizontal_length)
        
        layout.addRow('Horizontal length', self.hor_len_setting_widget)
        self.vert_len_settings_widget = QSpinBox()
        self.vert_len_settings_widget.setRange(1,1000)
        self.vert_len_settings_widget.setValue(self._vertical_length)
        
        layout.addRow('Vertical length', self.vert_len_settings_widget)
        self.always_centered_checkbox = QCheckBox()
        self.always_centered_checkbox.setChecked(self._always_centered)
        layout.addRow('Always centered', self.always_centered_checkbox)

        hbox = QHBoxLayout()
        self.x_pos_widget = QSpinBox()
        self.x_pos_widget.setRange(-10000, 10000)
        self.x_pos_widget.setValue(self._pos.x())
        
        self.y_pos_widget = QSpinBox()
        self.y_pos_widget.setRange(-10000, 10000)
        self.y_pos_widget.setValue(self._pos.y())
        
        hbox.addWidget(self.x_pos_widget)
        hbox.addWidget(self.y_pos_widget)
        layout.addRow('Position', hbox)

        groupBox.setLayout(layout)
        return groupBox

    def save_settings(self, settings_groupbox) -> None:
        self._color = self.color_setting_widget.color()
        self._horizontal_length = int(self.hor_len_setting_widget.value())
        self._vertical_length = int(self.vert_len_settings_widget.value())
        self._always_centered = self.always_centered_checkbox.isChecked()
        self._pos.setX(self.x_pos_widget.value())
        self._pos.setY(self.y_pos_widget.value())
        self._paint_crosshair(self.parent.scene)