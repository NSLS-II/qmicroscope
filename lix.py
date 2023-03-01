import sys

from qtpy.QtCore import (
    QPoint,
    QSettings,
    QSize,
)

from qtpy.QtWidgets import (
    QCheckBox,
    QComboBox,
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

from microscope.microscope import Microscope


class Form(QMainWindow):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        # Create widgets
        self.setWindowTitle("LIX Microscope Demo")

        # Create three microscopes in a list, and then lay them out.
        self.microscopes = [Microscope(self), Microscope(self), Microscope(self)]
        self.microscope = self.microscopes[0]
        self.names = ["Bob (0)", "Alice (1)", "Terry (2)"]
        self.buttons = []

        # Create a form with some controls
        self.selector = QComboBox()
        for m, n in zip(self.microscopes, self.names):
            self.selector.addItem(n, m)
            self.buttons.append(QPushButton(f"Start {n}"))

        self.fps = QSpinBox()
        self.fps.setRange(1, 30)
        self.fps.setValue(5)
        self.xDivs = QSpinBox()
        self.xDivs.setRange(1, 50)
        self.xDivs.setValue(5)
        self.yDivs = QSpinBox()
        self.yDivs.setRange(1, 50)
        self.yDivs.setValue(5)
        self.color = QCheckBox()

        self.url = QLineEdit("http://localhost:9998/jpg/image.jpg")

        self.button = QPushButton("Start")

        # Lay it out
        formLayout = QFormLayout()
        formLayout.addRow("Active Camera:", self.selector)
        formLayout.addRow("Camera URL:", self.url)
        formLayout.addRow("Frame Rate:", self.fps)
        formLayout.addRow("X Divisions:", self.xDivs)
        formLayout.addRow("Y Divisions:", self.yDivs)
        formLayout.addRow("Color boxes:", self.color)

        # Create layout and add widgets
        layout = QVBoxLayout()
        mbox = QHBoxLayout()
        for m in self.microscopes:
            mbox.addWidget(m)
        layout.addLayout(mbox)
        hbox = QHBoxLayout()
        hbox.addLayout(formLayout)
        hbox.addStretch()
        layout.addLayout(hbox)
        buttonBox = QHBoxLayout()
        for b in self.buttons:
            buttonBox.addWidget(b)
        layout.addLayout(buttonBox)

        # Set main windows widget using our central layout
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Add button signal to slot to start/stop
        self.buttons[0].clicked.connect(self.button0Pressed)
        self.buttons[1].clicked.connect(self.button1Pressed)
        self.buttons[2].clicked.connect(self.button2Pressed)

        # Connect to the microscope ROI clicked signal
        self.microscope.roiClicked.connect(self.onRoiClicked)

        # Listen for changes to the combo box
        self.selector.currentIndexChanged.connect(self.selectionChanged)

        # Read the settings and persist them
        settings = QSettings()
        self.readSettings(settings)

    # event : QCloseEvent
    def closeEvent(self, event):
        settings = QSettings()
        self.writeSettings(settings)
        event.accept()

    def selectionChanged(self, index):
        # Change the active microscope, need to define what this means...
        self.updateMicroscope()
        self.microscope = self.microscopes[index]
        self.updateForm()

    def button0Pressed(self):
        # Currently being a little lame - only update state on start/stop.
        self.buttonPressed(0)

    def button1Pressed(self):
        # Currently being a little lame - only update state on start/stop.
        self.buttonPressed(1)

    def button2Pressed(self):
        # Currently being a little lame - only update state on start/stop.
        self.buttonPressed(2)

    def buttonPressed(self, index):
        # Currently being a little lame - only update state on start/stop.
        if self.buttons[index].text() == f"Start {self.names[index]}":
            self.updateMicroscope()
            self.microscopes[index].acquire(True)
            self.buttons[index].setText(f"Stop {self.names[index]}")
        else:
            self.microscopes[index].acquire(False)
            self.buttons[index].setText(f"Start {self.names[index]}")

    def onRoiClicked(self, x, y):
        print(f"ROI: {x}, {y}")

    def updateMicroscope(self):
        self.microscope.url = self.url.text()
        self.microscope.fps = self.fps.value()
        self.microscope.xDivs = self.xDivs.value()
        self.microscope.yDivs = self.yDivs.value()
        self.microscope.color = self.color.isChecked()

    def updateForm(self):
        self.url.setText(self.microscope.url)
        self.fps.setValue(self.microscope.fps)
        self.xDivs.setValue(self.microscope.xDivs)
        self.yDivs.setValue(self.microscope.yDivs)
        self.color.setChecked(self.microscope.color)

    def readSettings(self, settings):
        """Load the application's settings."""
        settings.beginGroup("MainWindow")
        self.resize(settings.value("size", QSize(400, 400)))
        self.move(settings.value("pos", QPoint(200, 200)))
        settings.beginGroup("Microscope0")
        self.microscopes[0].readSettings(settings)
        # Also need to restore the settings to the form elements.
        self.updateForm()
        settings.endGroup()
        settings.beginGroup("Microscope1")
        self.microscopes[1].readSettings(settings)
        settings.endGroup()
        settings.beginGroup("Microscope2")
        self.microscopes[2].readSettings(settings)
        settings.endGroup()
        settings.endGroup()

    def writeSettings(self, settings):
        """Save the applications's settings persistently."""
        settings.beginGroup("MainWindow")
        settings.setValue("size", self.size())
        settings.setValue("pos", self.pos())
        self.updateMicroscope()
        settings.beginGroup("Microscope0")
        self.microscopes[0].writeSettings(settings)
        print(f"Microscope0: {self.microscopes[0].writeToDict()}")
        settings.endGroup()
        settings.beginGroup("Microscope1")
        self.microscopes[1].writeSettings(settings)
        settings.endGroup()
        settings.beginGroup("Microscope2")
        self.microscopes[2].writeSettings(settings)
        settings.endGroup()
        settings.endGroup()


if __name__ == "__main__":
    # Set up some application basics for saving settings
    QApplication.setOrganizationName("BNL")
    QApplication.setOrganizationDomain("bnl.gov")
    QApplication.setApplicationName("LIXMicroscope")

    # Create the Qt Application
    app = QApplication(sys.argv)

    # Create and show the form
    form = Form()
    form.show()

    # Run the main Qt loop
    sys.exit(app.exec_())
