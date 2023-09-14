import sys

from qtpy.QtCore import (
    QPoint,
    QSettings,
    QSize,
)

from qtpy.QtWidgets import (
    QCheckBox,
    QLineEdit,
    QPushButton,
    QApplication,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QSpinBox,
    QMainWindow,
    QWidget,
)

from qmicroscope.microscope import Microscope
from qmicroscope.container import Container
from qmicroscope.settings import Settings
from qmicroscope.plugins.record_plugin import RecordPlugin


class Form(QMainWindow):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        # Create widgets
        self.setWindowTitle("NSLS-II Microscope Widget")
        self.container = Container(self, plugins=[RecordPlugin])
        self.container.count = 3
        self.container.size = [2, 2]
        self.microscope = self.container.microscope(0)
        # self.microscope = Microscope(self)

        self.startButton = QPushButton("Start")
        self.settingsButton = QPushButton("Settings")

        # Create layout and add widgets
        layout = QVBoxLayout()
        hButtonBox = QHBoxLayout()
        hButtonBox.addStretch()
        hButtonBox.addWidget(self.startButton)
        hButtonBox.addWidget(self.settingsButton)
        hButtonBox.addStretch()
        layout.addLayout(hButtonBox)
        layout.addWidget(self.container)

        # Set main windows widget using our central layout
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Add button signal to slot to start/stop
        self.startButton.clicked.connect(self.startButtonPressed)
        self.settingsButton.clicked.connect(self.settingsButtonClicked)

        # Connect to the microscope ROI clicked signal
        if self.microscope:
            self.microscope.roiClicked.connect(self.onRoiClicked)

        # Read the settings and persist them
        settings = QSettings("NSLS2", "main")
        self.readSettings(settings)

        self.settingsDialog = Settings(self)
        self.settingsDialog.setContainer(self.container)

    # event : QCloseEvent
    def closeEvent(self, event):
        settings = QSettings("NSLS2", "main")
        self.writeSettings(settings)
        event.accept()

    def startButtonPressed(self):
        # Currently being a little lame - only update state on start/stop.
        print("Button pressed!", self.startButton.text())
        if self.startButton.text() == "Start":
            self.container.start(True)
            self.startButton.setText("Stop")
        else:
            self.container.start(False)
            self.startButton.setText("Start")

    def settingsButtonClicked(self):
        # Open the settings dialog.
        self.settingsDialog.show()

    def onRoiClicked(self, x, y):
        print(f"ROI: {x}, {y}")

    def readSettings(self, settings):
        """Load the application's settings."""
        settings.beginGroup("MainWindow")
        self.resize(settings.value("size", QSize(400, 400)))
        self.move(settings.value("pos", QPoint(200, 200)))
        self.container.readSettings(settings)
        settings.endGroup()

    def writeSettings(self, settings):
        """Save the applications's settings persistently."""
        settings.beginGroup("MainWindow")
        settings.setValue("size", self.size())
        settings.setValue("pos", self.pos())
        self.container.writeSettings(settings)
        settings.endGroup()


if __name__ == "__main__":
    # Set up some application basics for saving settings
    QApplication.setOrganizationName("BNL")
    QApplication.setOrganizationDomain("bnl.gov")
    QApplication.setApplicationName("QCamera")

    # Create the Qt Application
    app = QApplication(sys.argv)

    # Create and show the form
    form = Form()
    form.show()

    # Run the main Qt loop
    sys.exit(app.exec_())
