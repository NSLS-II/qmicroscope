from collections import defaultdict
from typing import TYPE_CHECKING, Any, Dict, Optional

from qtpy.QtCore import QObject, QPoint, QRect, QRectF, Qt, Signal
from qtpy.QtGui import QColor, QMouseEvent, QPen
from qtpy.QtWidgets import (
    QAction,
    QColorDialog,
    QFormLayout,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSceneMouseEvent,
    QGroupBox,
    QSpinBox,
)

from qmicroscope.plugins.base_plugin import BasePlugin
from qmicroscope.widgets.color_button import ColorButton
from qmicroscope.widgets.rubberband import ResizableRubberBand

if TYPE_CHECKING:
    from qmicroscope.microscope import Microscope


class CellSignal(QObject):
    clicked = Signal(object)


class CellGraphicsItem(QGraphicsRectItem):
    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mousePressEvent(event)
        self.setPen(QColor("red"))
        self.setZValue(1)
        self.cell_signal.clicked.emit(self)


class SquareGridPlugin(BasePlugin):
    """A plugin for displaying a grid on an image in a microscope application.

    The grid can be defined by drawing a rectangle on the image,
    and the color and number of divisions in the grid can be customized.
    The plugin also provides options for showing and hiding the grid and the rectangle used to define it.

    """

    def __init__(self, parent: "Optional[Microscope]" = None):
        """Initializes the GridPlugin instance.

        Args:
            parent (Optional[Microscope]): The microscope application that the plugin is attached to.
        """
        super().__init__(parent)
        self.name = "Selectable Grid"
        self.rubberBand: "Optional[ResizableRubberBand]" = None
        self.parent = parent
        self.start: QPoint = QPoint(0, 0)
        self.end: QPoint = QPoint(1, 1)
        self.start_grid = False
        self._grid_color = QColor.fromRgb(0, 255, 0)
        self._grid_items = []
        self._grid = None
        self.plugin_state = defaultdict(bool)
        self._cell_size = 10
        self.selected_cell = None
        self.cell_signal = CellSignal()
        self.cell_signal.clicked.connect(self.handle_cell_clicked)

    @property
    def brush_color(self):
        if self._grid_color:
            return self._grid_color
        else:
            return QColor.fromRgb(0, 255, 0)

    def convert_str_bool(self, val):
        """Converts a string representation of a boolean to a boolean value.

        Args:
            val (str): The string representation of the boolean.

        Returns:
            bool: The boolean value.
        """
        if isinstance(val, str):
            return True if val.lower() == "true" else False
        return val

    def read_settings(self, settings: Dict[str, Any]):
        """Reads the plugin's settings from a dictionary.

        Args:
            settings (Dict[str, Any]): A dictionary containing the settings.
        """
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
        self._cell_size = int(settings.get("cell_size", 10))

    def write_settings(self) -> Dict[str, Any]:
        """Writes the plugin's settings to a dictionary.

        Returns:
            Dict[str, Any]: A dictionary containing the settings.
        """
        settings_values = {}
        settings_values["color"] = self._grid_color
        settings_values["start"] = self.start
        settings_values["end"] = self.end
        settings_values["grid_hidden"] = self.plugin_state["grid_hidden"]
        settings_values["selector_hidden"] = self.plugin_state["selector_hidden"]
        settings_values["grid_defined"] = self.plugin_state["grid_defined"]
        settings_values["cell_size"] = self._cell_size
        return settings_values

    def add_settings(self, parent=None) -> Optional[QGroupBox]:
        """
        Create a new QGroupBox containing settings widgets for the grid plugin.

        Parameters:
            parent (QWidget): The parent widget for the QGroupBox. If None, the parent widget is set
                to the parent widget of the plugin.

        Returns:
            Optional[QGroupBox]: The new QGroupBox object.
        """
        parent = parent if parent else self.parent
        groupBox = QGroupBox(self.name, parent)
        layout = QFormLayout()
        self.color_setting_widget = ColorButton(parent=parent, color=self._grid_color)
        layout.addRow("Color", self.color_setting_widget)

        self.cell_size_widget = QSpinBox()
        self.cell_size_widget.setRange(1, 10000)
        self.cell_size_widget.setValue(self._cell_size)

        layout.addRow("Cell Size", self.cell_size_widget)
        groupBox.setLayout(layout)
        return groupBox

    def save_settings(self, settings_groupbox) -> None:
        """
        Save the settings values from the specified QGroupBox to the corresponding class variables,
        and update the grid using the new settings.

        Parameters:
            settings_groupbox (QGroupBox): The QGroupBox containing the settings widgets.

        Returns:
            None.
        """
        self._grid_color = self.color_setting_widget.color()
        self._cell_size = self.cell_size_widget.value()

        self.paintBoxes(self.parent.scene)

    def start_plugin(self):
        """Starts the plugin."""
        if self.plugin_state["grid_defined"]:
            self.paintBoxes(self.parent.scene)
            # self._grid.setVisible(not self.plugin_state["grid_hidden"])
            for item in self._grid_items:
                item.setVisible(not self.plugin_state["grid_hidden"])
            self.create_rubberband()
            self.rubberBand.setGeometry(QRect(self.start, self.end).normalized())
            self.rubberBand.setVisible(not self.plugin_state["selector_hidden"])

    def stop_plugin(self):
        """Stops the plugin."""
        self.remove_grid(self.parent.scene)
        if self.rubberBand:
            self.rubberBand.destroy()

    def context_menu_entry(self):
        """Returns a list of QAction objects representing the plugin's context menu options.

        Returns:
            List[QAction]: The list of QAction objects.
        """
        actions = []
        if self.plugin_state["grid_defined"]:
            self.hide_show_action = QAction(
                "Selector Visible",
                self.parent,
                checkable=True,
                checked=self.rubberBand.isVisible(),
            )
            self.hide_show_action.triggered.connect(self._toggle_selector)
            actions.append(self.hide_show_action)
            self.hide_show_grid_action = QAction(
                "Grid Visible",
                self.parent,
                checkable=True,
                checked=not self.plugin_state["grid_hidden"],
            )
            self.hide_show_grid_action.triggered.connect(self._toggle_grid)
            actions.extend([self.hide_show_grid_action])
        self.start_drawing_grid_action = QAction("Draw grid", self.parent)
        self.start_drawing_grid_action.triggered.connect(self._start_grid)
        actions.append(self.start_drawing_grid_action)

        return actions

    def mouse_move_event(self, event: QMouseEvent):
        """Handle mouse move events. If the grid is being defined and a rubberband object exists and the
        left mouse button is pressed, updates the rubberband object's position and the end position
        of the grid.

        Parameters:
            event (QMouseEvent): The mouse move event.

        Returns:
            None.
        """
        if self.start_grid:
            if self.rubberBand and event.buttons() == Qt.LeftButton:
                if self.rubberBand.isVisible():
                    self.rubberBand.setGeometry(
                        QRect(self.start, event.pos()).normalized()
                    )
                    self.end = event.pos()

    def mouse_press_event(self, event: QMouseEvent):
        """
        Handle mouse press events. If the grid is being defined and the left mouse button is pressed,
        sets the start position of the grid. If a rubberband object does not exist and the viewport does
        not exist, creates a new rubberband object.

        Parameters:
            event (QMouseEvent): The mouse press event.

        Returns:
            None.
        """
        if self.start_grid:
            if event.buttons() == Qt.LeftButton:
                self.start = event.pos()

            if not self.rubberBand:
                self.create_rubberband()

    def mouse_release_event(self, event: QMouseEvent):
        if self.start_grid:
            self.paintBoxes(self.parent.scene)
            self.plugin_state["grid_defined"] = True
            self.start_grid = False

    def _select_grid_color(self) -> None:
        """Shows a color picker dialog and sets the grid color to the selected color."""
        self._grid_color = QColorDialog.getColor()
        if self._grid:
            self.paintBoxes(self.parent.scene)

    def _toggle_selector(self):
        """Toggles the visibility of the rectangle used to define the grid."""
        self.rubberBand.toggle_selector()
        self.plugin_state["selector_hidden"] = not self.rubberBand.isVisible()

    def _toggle_grid(self) -> None:
        """Toggles the visibility of the grid."""
        if self._grid_items:
            for item in self._grid_items:
                if item.isVisible():
                    item.hide()
                else:
                    item.show()

            self.plugin_state["grid_hidden"] = not self.plugin_state["grid_hidden"]

    def _start_grid(self):
        """Sets the start_grid flag to True."""
        self.start_grid = True

    def update_grid(self, start: QPoint, end: QPoint) -> None:
        """Updates the grid based on the new start and end points of the rectangle used to define it.

        Args:
            start (QPoint): The new starting point.
            end (QPoint): The new ending point.
        """
        self.start = start
        self.end = end
        self.paintBoxes(self.parent.scene)

    def remove_grid(self, scene: QGraphicsScene):
        """
        Remove the current grid from the specified QGraphicsScene if it exists.

        Parameters:
            scene (QGraphicsScene): The QGraphicsScene from which to remove the grid.

        Returns:
            None.
        """
        if self._grid_items:
            for item in self._grid_items:
                scene.removeItem(item)
        self._grid_items = []

    def create_rubberband(self):
        """
        Create a new rubberband object and display it on the parent widget.

        Returns:
            None.
        """
        self.rubberBand = ResizableRubberBand(self.parent)
        self.rubberBand.box_modified.connect(self.update_grid)
        self.rubberBand.setGeometry(QRect(self.start, self.end))
        self.rubberBand.show()

    def paintBoxes(self, scene: QGraphicsScene) -> None:
        """
        Paint the boxes of the grid onto the specified QGraphicsScene. Removes the old grid if it
        exists, creates a new grid using the current rubberband object's position and settings,
        and adds the new grid to the specified QGraphicsScene.

        Parameters:
            scene (QGraphicsScene): The QGraphicsScene onto which to paint the grid.

        Returns:
            None.
        """
        self.remove_grid(scene)
        rect = QRectF(self.start, self.end)
        pen = QPen(self.brush_color)
        # self._grid_items.append(scene.addRect(rect, pen=pen))
        # Now draw the lines for the boxes in the rectangle.
        x1 = self.start.x()
        y1 = self.start.y()
        x2 = self.end.x()
        y2 = self.end.y()

        num_rows = int(abs(y2 - y1) / self._cell_size)
        num_cols = int(abs(x2 - x1) / self._cell_size)
        self._grid_cells: "list[list[CellGraphicsItem]]" = []
        center_x = (x2 - x1) / 2
        center_y = (y2 - y1) / 2

        for c in range(num_cols):
            row = []
            for r in range(num_rows):
                top_left = QPoint(
                    x1 + (c * self._cell_size), y1 + (r * self._cell_size)
                )
                bot_right = QPoint(
                    x1 + ((c + 1) * self._cell_size), y1 + ((r + 1) * self._cell_size)
                )
                # cell_def = QRectF(top_left, bot_right)
                # cell = scene.addRect(cell_def, pen=pen)
                # cell = CellGraphicsItem(cell_def)
                cell = CellGraphicsItem(0, 0, self._cell_size, self._cell_size)
                cell.setPos(top_left)
                cell.setTransformOriginPoint(center_x, center_y)
                cell.cell_signal = self.cell_signal
                cell.setPen(pen)
                scene.addItem(cell)
                cell.setToolTip(f"Row: {r}\n Col: {c}")
                self._grid_items.append(cell)
                row.append(cell)
            self._grid_cells.append(row)

    def handle_cell_clicked(self, cell: CellGraphicsItem):
        if self.selected_cell:
            self.selected_cell.setPen(self.brush_color)
            self.selected_cell.setZValue(0)
        cell.setPen(QColor("red"))
        cell.setZValue(1)
        self.selected_cell = cell
        self.scale(2.0)

    def scale(self, scale_factor):
        x1 = self.start.x()
        y1 = self.start.y()
        for r, row in enumerate(self._grid_cells):
            for c, cell in enumerate(row):
                cell.setScale(scale_factor)
                top_left = QPoint(
                    x1 + (c * self._cell_size * scale_factor),
                    y1 + (r * self._cell_size * scale_factor),
                )
                cell.setPos(top_left)
