from qtpy.QtWidgets import QWidget, QGridLayout
from qtpy.QtGui import QPaintEvent
from qtpy.QtCore import QSettings
from qmicroscope.microscope import Microscope
from typing import List

""" A widget that contains one or more microscope widgets in a grid. """


class Container(QWidget):
    def __init__(self, parent: "QWidget|None" = None, plugins=None):
        super(Container, self).__init__(parent)
        if not plugins:
            self.plugins = []
        else:
            self.plugins = plugins
        self.parent_widget = parent
        self._update: bool = True  # Is an update required
        self._count: int = 1  # The number of widgets contained
        self._size = [1, 1]  # The size of the container in widgets
        self._horizontal: bool = True  # When setting the count prefer horizontal

        self._widgets: "List[Microscope]" = []
        microscope_widget = Microscope(self, plugins=self.plugins)
        if hasattr(self.parent_widget, "setup_main_microscope"):
            microscope_widget.clicked_url.connect(
                self.parent_widget.setup_main_microscope
            )
        # else:
        # microscope_widget = Microscope(self, viewport=False, plugins=self.plugins)

        self._widgets.append(microscope_widget)

        self._grid = QGridLayout()
        self._grid.setSpacing(1)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._grid)
        self.layout().addWidget(self._widgets[0])

    def microscope(self, num: int) -> "Microscope|None":
        if num > len(self._widgets):
            return None
        return self._widgets[num]

    @property
    def count(self) -> int:
        return self._count

    @count.setter
    def count(self, new_count):
        if self._count != new_count:
            self._update = True

        if new_count > 1:
            self._count = new_count
        else:
            self._count = 1

        if not self._horizontal:
            self._size = [self._count, 1]
        else:
            self._size = [1, self._count]

    @property
    def size(self) -> List[int]:
        return self._size

    @size.setter
    def size(self, new_size):
        if self._size != new_size:
            self._update = True
            self._size = new_size
            self._count = new_size[0] * new_size[1]

    @property
    def horizontal(self) -> bool:
        return self._horizontal

    @horizontal.setter
    def horizontal(self, new_value):
        if self._horizontal != new_value:
            self._update = True
            self._horizontal = new_value

    @property
    def vertical(self):
        return not self._horizontal

    @horizontal.setter
    def horizontal(self, new_value):
        if self._horizontal == new_value:
            self._update = True
            self._horizontal = not new_value

    def start(self, acq) -> None:
        """Start all of the camera widgets."""
        for m in self._widgets:
            m.acquire(acq)

    def updateWidgets(self) -> None:
        """Instantiate/show objects."""
        if len(self._widgets) > self._count:
            self._widgets = self._widgets[: self._count]
        while len(self._widgets) < self._count:
            microscope_widget = Microscope(self, plugins=self.plugins)
            if hasattr(self.parent_widget, "setup_main_microscope"):
                microscope_widget.clicked_url.connect(
                    self.parent_widget.setup_main_microscope
                )
            self._widgets.append(microscope_widget)

    def paintEvent(self, event: QPaintEvent) -> None:
        if self._update:
            print("updating")
            # We need to update the number of widgets, get the layout right.
            self.updateWidgets()
            # Now update the layout of the widget!
            _cur = 0
            self._grid = QGridLayout()
            self._grid.setSpacing(1)
            self._grid.setContentsMargins(0, 0, 0, 0)
            print(self._size)
            for i in range(self._size[0]):
                for j in range(self._size[1]):
                    if _cur < len(self._widgets):
                        self._grid.addWidget(self._widgets[_cur], j, i)
                    _cur = _cur + 1
            print(self._grid.rowCount())

            QWidget().setLayout(self.layout())
            self.setLayout(self._grid)
            self._update = False

    def readSettings(self, settings: QSettings) -> None:
        """Load the application's settings."""
        settings.beginGroup("Container")
        sz = [1, 1]
        sz[0] = settings.value("cols", 1, type=int)
        sz[1] = settings.value("rows", 1, type=int)
        self.size = sz
        # Ensure the widgets are created, then load their settings.
        self.updateWidgets()
        for i in range(len(self._widgets)):
            settings.beginGroup(f"Camera{i}")
            self._widgets[i].readSettings(settings)
            settings.endGroup()

        settings.endGroup()

    def writeSettings(self, settings: QSettings) -> None:
        """Save the applications's settings persistently."""
        settings.beginGroup("Container")
        settings.setValue("cols", self._size[0])
        settings.setValue("rows", self._size[1])
        # self.updateMicroscope()
        # Write out all the settings for the widgets.
        for i in range(len(self._widgets)):
            self._widgets[i].writeSettings(settings, settings_group=f"Camera{i}")

        settings.endGroup()
