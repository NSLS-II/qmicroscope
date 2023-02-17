from microscope.plugins.base_plugin import BaseImagePlugin
from qtpy.QtGui import QColor, QPen, QMouseEvent, QFont, QBrush
from qtpy.QtCore import QPoint, QLineF
from qtpy.QtWidgets import (QGraphicsScene, QAction, QColorDialog, 
                            QGroupBox, QFormLayout, QSpinBox,
                            QCheckBox, QHBoxLayout, QLineEdit, QGraphicsSimpleTextItem)
from typing import Dict, Any, Optional, TYPE_CHECKING
from microscope.widgets.color_button import ColorButton
if TYPE_CHECKING:
    from microscope.microscope import Microscope

class ScalePlugin(BaseImagePlugin):
    def __init__(self, parent: "Microscope") -> None:
        super().__init__(parent)
        self.name = 'Scale'
        self._color = QColor.fromRgb(0, 255, 0)
        self._pos = None
        self._horizontal_length = 100
        self._vertical_length = 100
        self._visible = True
        self._hor_line = None
        self._vert_line = None
        self._hor_line_measure = '100 cm'
        self._vert_line_measure = '100 cm'
        self._hor_line_measure_text = QGraphicsSimpleTextItem()
        self._vert_line_measure_text = QGraphicsSimpleTextItem()
        _font = QFont()
        _font.setPixelSize(20)
        _font.setBold(False)

        self._hor_line_measure_text.setFont(_font)
        self._vert_line_measure_text.setFont(_font)

    def _paint_scale(self, scene: QGraphicsScene):
        for item in [self._hor_line, self._vert_line, 
                     self._hor_line_measure_text, self._vert_line_measure_text]:
            if item:
                scene.removeItem(item)
        if self._pos is None:
            self._pos = QPoint(int(self.parent.view.width() - 30), 
                           int(self.parent.view.height() - 30))

        pen = QPen(self._color)
        start_point = self._pos
        end_point = self._pos + QPoint(int(self._horizontal_length),0) 
        hor_line = QLineF(start_point, end_point)
        self._hor_line = scene.addLine(hor_line, pen)

        start_point = self._pos 
        end_point = self._pos - QPoint(0, int(self._vertical_length))
        vert_line = QLineF(start_point, end_point)
        self._vert_line = scene.addLine(vert_line, pen)

        
        self._hor_line_measure_text.setText(self._hor_line_measure)
        self._hor_line_measure_text.setBrush(QBrush(self._color))
        self._hor_line_measure_text.setPos(self._pos)

        self._vert_line_measure_text.setText(self._vert_line_measure)
        self._vert_line_measure_text.setBrush(QBrush(self._color))
        self._vert_line_measure_text.setPos(self._pos - QPoint(25,0))
        self._vert_line_measure_text.setRotation(-90)

        scene.addItem(self._hor_line_measure_text)
        scene.addItem(self._vert_line_measure_text)
        

        self._toggle_visibility(self._visible)

    
    def _toggle_visibility(self, value):
        self._visible = value

        for item in [self._hor_line, self._vert_line, 
                     self._hor_line_measure_text, self._vert_line_measure_text]:
            item.setVisible(self._visible)


    def _change_color(self):
        self._color = QColorDialog.getColor()
        self._paint_crosshair(self.parent.scene)

    def context_menu_entry(self):
        actions = []
        visible_action = QAction('Visible', self.parent, checkable=True, checked=self._visible)
        visible_action.triggered.connect(self._toggle_visibility)
        actions.append(visible_action)
        return actions

    def mouse_press_event(self, event: QMouseEvent):
        pass

    def mouse_move_event(self, event: QMouseEvent):
        pass

    def mouse_release_event(self, event: QMouseEvent):
        pass

    def read_settings(self, settings: Dict[str, Any]):
        self._color = settings.get('color', self._color)
        self._pos = settings.get('pos', self._pos)
        self._horizontal_length = int(settings.get('hor_len', self._horizontal_length))
        self._vertical_length = int(settings.get('vert_len', self._vertical_length))
        self._visible = settings.get('visible', self._visible)
        self._hor_line_measure = settings.get('hor_line_measure')
        self._vert_line_measure = settings.get('vert_line_measure')
        if isinstance(self._visible, str):
            self._visible = True if self._visible.lower() == 'true' else False
        self._paint_scale(self.parent.scene)

    def write_settings(self) -> Dict[str, Any]:
        settings = {}
        settings['color'] = self._color
        settings['pos'] = self._pos
        settings['hor_len'] = self._horizontal_length
        settings['vert_len'] = self._vertical_length
        settings['visible'] = self._visible
        settings['hor_line_measure'] = self._hor_line_measure
        settings['vert_line_measure'] = self._vert_line_measure
        return settings

    def add_settings(self, parent=None) -> Optional[QGroupBox]:
        parent = parent if parent else self.parent
        groupBox = QGroupBox(self.name, parent)
        layout = QFormLayout()
        self.color_setting_widget = ColorButton(parent=parent, color=self._color) 
        layout.addRow('Color', self.color_setting_widget)
        self.hor_len_setting_widget = QSpinBox()
        self.hor_len_setting_widget.setRange(0, 1000)
        self.hor_len_setting_widget.setValue(self._horizontal_length)
        layout.addRow('Horizontal length', self.hor_len_setting_widget)
        self.vert_len_settings_widget = QSpinBox()
        self.vert_len_settings_widget.setRange(0,1000)
        self.vert_len_settings_widget.setValue(self._vertical_length)
        layout.addRow('Vertical length', self.vert_len_settings_widget)

        self.hor_measure_setting_widget = QLineEdit(self._hor_line_measure)
        layout.addRow('Horizontal measure', self.hor_measure_setting_widget)

        self.vert_measure_setting_widget = QLineEdit(self._vert_line_measure)
        layout.addRow('Vertical measure', self.vert_measure_setting_widget)

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
        self._pos.setX(self.x_pos_widget.value())
        self._pos.setY(self.y_pos_widget.value())
        self._hor_line_measure = self.hor_measure_setting_widget.text()
        self._vert_line_measure = self.vert_measure_setting_widget.text()
        self._paint_scale(self.parent.scene)