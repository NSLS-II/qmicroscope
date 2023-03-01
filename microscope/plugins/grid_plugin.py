from typing import Optional, Dict, Any, TYPE_CHECKING
from qtpy.QtWidgets import (
    QAction,
    QColorDialog,
    QGraphicsScene,
    QGroupBox,
    QFormLayout,
    QHBoxLayout,
    QSpinBox,
    QLabel,
)
from qtpy.QtCore import QPoint, Qt, QRect, QRectF
from qtpy.QtGui import QColor, QPen
from microscope.widgets.rubberband import ResizableRubberBand
from microscope.widgets.color_button import ColorButton
from microscope.plugins.base_plugin import BasePlugin
from qtpy.QtGui import QMouseEvent
from collections import defaultdict

if TYPE_CHECKING:
    from microscope.microscope import Microscope


class GridPlugin(BasePlugin):
    def __init__(self, parent: "Optional[Microscope]" = None):
        super().__init__(parent)
        self.name = "Grid"
        self.rubberBand: "Optional[ResizableRubberBand]" = None
        self.parent = parent
        self.start: QPoint = QPoint(0, 0)
        self.end: QPoint = QPoint(1, 1)
        self.start_grid = False
        self._grid_color = QColor.fromRgb(0, 255, 0)
        self._grid_items = []
        self._grid = None
        self.plugin_state = defaultdict(bool)
        self._x_divs = 5
        self._y_divs = 5

    def convert_str_bool(self, val):
        if isinstance(val, str):
            return True if val.lower() == "true" else False
        return val

    def read_settings(self, settings: Dict[str, Any]):

        self._grid_color = settings.get("color", QColor.fromRgb(0, 255, 0))
        self.start = settings.get("start", QPoint(0, 0))
        self.end = settings.get("end", QPoint(1, 1))
        self.plugin_state["grid_hidden"] = self.convert_str_bool(
            settings.get("grid_hidden", False)
        )
        self.plugin_state["selector_hidden"] = self.convert_str_bool(
            settings.get("selector_hidden", False)
        )
        self.plugin_state["grid_defined"] = self.convert_str_bool(
            settings.get("grid_defined", False)
        )
        self._x_divs = int(settings.get("x_divs", 5))
        self._y_divs = int(settings.get("y_divs", 5))

    def start_plugin(self):
        if self.plugin_state["grid_defined"]:
            self.paintBoxes(self.parent.scene)
            self._grid.setVisible(not self.plugin_state["grid_hidden"])
            self.create_rubberband()
            self.rubberBand.setGeometry(QRect(self.start, self.end).normalized())
            self.rubberBand.setVisible(not self.plugin_state["selector_hidden"])

    def stop_plugin(self):
        self.remove_grid(self.parent.scene)
        if self.rubberBand:
            self.rubberBand.destroy()

    def write_settings(self) -> Dict[str, Any]:
        settings_values = {}
        settings_values["color"] = self._grid_color
        settings_values["start"] = self.start
        settings_values["end"] = self.end
        settings_values["grid_hidden"] = self.plugin_state["grid_hidden"]
        settings_values["selector_hidden"] = self.plugin_state["selector_hidden"]
        settings_values["grid_defined"] = self.plugin_state["grid_defined"]
        settings_values["x_divs"] = self._x_divs
        settings_values["y_divs"] = self._y_divs
        return settings_values

    def context_menu_entry(self):

        actions = []
        if self.plugin_state["grid_defined"]:
            # if not self.rubberBand:
            #    self.create_rubberband()
            #    self.rubberBand.setVisible(self.plugin_state['selector_hidden'])
            self.hide_show_action = QAction(
                "Selector Visible",
                self.parent,
                checkable=True,
                checked=self.rubberBand.isVisible(),
            )
            self.hide_show_action.triggered.connect(self._toggle_selector)
            actions.append(self.hide_show_action)
            # if self._grid:
            self.hide_show_grid_action = QAction(
                "Grid Visible",
                self.parent,
                checkable=True,
                checked=self._grid.isVisible(),
            )
            # self.select_grid_color_action = QAction('Change Grid color', self.parent)
            self.hide_show_grid_action.triggered.connect(self._toggle_grid)
            # self.select_grid_color_action.triggered.connect(self._select_grid_color)
            actions.extend(
                [self.hide_show_grid_action]
            )  # , self.select_grid_color_action])

        self.start_drawing_grid_action = QAction("Draw grid", self.parent)
        self.start_drawing_grid_action.triggered.connect(self._start_grid)
        actions.append(self.start_drawing_grid_action)

        return actions

    def _select_grid_color(self) -> None:
        self._grid_color = QColorDialog.getColor()
        if self._grid:
            self.paintBoxes(self.parent.scene)

    def _toggle_selector(self):
        self.rubberBand.toggle_selector()
        self.plugin_state["selector_hidden"] = not self.rubberBand.isVisible()

    def _toggle_grid(self) -> None:
        if self._grid:
            if self._grid.isVisible():
                self._grid.hide()
                self.plugin_state["grid_hidden"] = True
            else:
                self._grid.show()
                self.plugin_state["grid_hidden"] = False

    def _start_grid(self):
        self.start_grid = True

    def update_grid(self, start: QPoint, end: QPoint) -> None:
        self.start = start
        self.end = end
        self.paintBoxes(self.parent.scene)

    def mouse_move_event(self, event: QMouseEvent):
        if self.start_grid:
            if self.rubberBand and event.buttons() == Qt.LeftButton:
                if self.rubberBand.isVisible():
                    self.rubberBand.setGeometry(
                        QRect(self.start, event.pos()).normalized()
                    )
                    self.end = event.pos()

    def mouse_press_event(self, event: QMouseEvent):
        if self.start_grid:
            if event.buttons() == Qt.LeftButton:
                self.start = event.pos()

            if not self.rubberBand and not self.parent.viewport:
                self.create_rubberband()

    def mouse_release_event(self, event: QMouseEvent):
        if self.start_grid:
            self.paintBoxes(self.parent.scene)
            self.plugin_state["grid_defined"] = True
            self.start_grid = False

    def remove_grid(self, scene: QGraphicsScene):
        if self._grid:
            if self._grid.scene() == scene:
                scene.removeItem(self._grid)
                self._grid = None
                self._grid_items = []

    def create_rubberband(self):
        self.rubberBand = ResizableRubberBand(self.parent)
        self.rubberBand.box_modified.connect(self.update_grid)
        self.rubberBand.setGeometry(QRect(self.start, self.end))
        self.rubberBand.show()

    def paintBoxes(self, scene: QGraphicsScene) -> None:
        self.remove_grid(scene)
        rect = QRectF(self.start, self.end)
        if self._grid_color:
            brushColor = self._grid_color
        else:
            brushColor = QColor.fromRgb(0, 255, 0)
        pen = QPen(brushColor)
        self._grid_items.append(scene.addRect(rect, pen=pen))
        # Now draw the lines for the boxes in the rectangle.
        x1 = self.start.x()
        y1 = self.start.y()
        x2 = self.end.x()
        y2 = self.end.y()
        inc_x = (x2 - x1) / self._x_divs
        inc_y = (y2 - y1) / self._y_divs

        for i in range(1, self._x_divs):
            l = scene.addLine(int(x1 + i * inc_x), y1, int(x1 + i * inc_x), y2, pen=pen)
            self._grid_items.append(l)
        for i in range(1, self._y_divs):
            l = scene.addLine(x1, int(y1 + i * inc_y), x2, int(y1 + i * inc_y), pen=pen)
            self._grid_items.append(l)

        self._grid = scene.createItemGroup(self._grid_items)

    def add_settings(self, parent=None) -> Optional[QGroupBox]:
        parent = parent if parent else self.parent
        groupBox = QGroupBox(self.name, parent)
        layout = QFormLayout()
        self.color_setting_widget = ColorButton(parent=parent, color=self._grid_color)
        layout.addRow("Color", self.color_setting_widget)

        hbox = QHBoxLayout()
        self.x_divs_widget = QSpinBox()
        self.x_divs_widget.setRange(1, 10000)
        self.x_divs_widget.setValue(self._x_divs)

        self.y_divs_widget = QSpinBox()
        self.y_divs_widget.setRange(1, 10000)
        self.y_divs_widget.setValue(self._y_divs)

        hbox.addWidget(self.x_divs_widget)
        label = QLabel("Y Divisions")
        hbox.addWidget(label)
        hbox.addWidget(self.y_divs_widget)

        layout.addRow("X Divisions", hbox)
        groupBox.setLayout(layout)
        return groupBox

    def save_settings(self, settings_groupbox) -> None:
        self._grid_color = self.color_setting_widget.color()
        self._x_divs = self.x_divs_widget.value()
        self._y_divs = self.y_divs_widget.value()

        self.paintBoxes(self.parent.scene)
