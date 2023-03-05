from typing import Dict, Any, TYPE_CHECKING, Optional
from qtpy.QtWidgets import (
    QAction,
    QGroupBox,
    QFormLayout,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QSpinBox,
    QLineEdit,
    QCheckBox,
)
from qtpy.QtGui import QImage, QPainter, QPen, QFont, QColor
from microscope.plugins.base_plugin import BaseImagePlugin
from microscope.widgets.color_button import ColorButton
from qtpy.QtGui import QMouseEvent
from qtpy.QtCore import QThread, Signal, QObject, Qt
import cv2 as cv
import numpy as np
from pathlib import Path
from datetime import datetime

if TYPE_CHECKING:
    from microscope.microscope import Microscope


class RecorderThread(QThread):
    def __init__(self):
        super().__init__()
        self.video_recorder = cv.VideoWriter()
        self.record = True
        self.width = 100
        self.height = 100
        self.fps = 5
        self.fourcc = cv.VideoWriter_fourcc(*"avc1")
        self.path = "output.mp4"

    def start(self, path, fourcc, fps, width, height):
        self.set_params(path, fourcc, fps, width, height)
        self._setup_recorder()
        super().start()

    def set_params(
        self, path="output.mp4", fourcc="avc1", fps=5, width=100, height=100
    ):
        self.width = width
        self.height = height
        if isinstance(fourcc, str):
            self.fourcc = cv.VideoWriter(*fourcc)
        else:
            self.fourcc = self.fourcc
        self.fps = fps
        self.path = path

    def _setup_recorder(self):
        self.video_recorder.open(
            str(self.path), self.fourcc, float(self.fps), (self.width, self.height)
        )

    def stop(self):
        self.video_recorder.release()
        self.record = False

    def run(self):
        while self.record:
            continue

    def write_frame(self, frame):
        if frame.shape[0] != self.height or frame.shape[1] != self.width:
            self.height = frame.shape[0]
            self.width = frame.shape[1]
            self.video_recorder.release()
            self._setup_recorder()
        # print(f'Frame shape: {frame.shape} w,d: {self.width} {self.height}')
        if self.video_recorder.isOpened():
            self.video_recorder.write(frame)


class RecordPlugin(QObject):
    image_ready = Signal(object)

    def __init__(self, parent: "Microscope") -> None:
        super().__init__(parent)
        # self.parent = parent
        self.name = "Record"
        self.fourcc = cv.VideoWriter_fourcc(*"H264")  # avc1 - mp4
        # self.filename = Path('/nsls2/data/fmx/legacy/2023-1/pass-312064/video_test/output')
        self.filename = Path.home() / Path("output")
        self.current_filepath = None
        self.file_extension = "mp4"
        self.recording = False
        self.fps = 5
        self.width = 480
        self.height = 480
        self.hours_per_file = 12
        self.number_of_files = 6
        self.video_recorder_thread = RecorderThread()
        self.image_ready.connect(self.video_recorder_thread.write_frame)
        self.updates_image = True
        self.raw_image = True
        self.timestamp = False
        self.timestamp_color = QColor.fromRgb(0, 255, 0)
        self.timestamp_font_size = 12

    def qimage_to_mat(self, incomingImage: QImage):
        """Converts a QImage into an opencv MAT format"""

        incomingImage = incomingImage.convertToFormat(QImage.Format.Format_RGB888)
        incomingImage = incomingImage.scaledToWidth(self.width)
        self.height = incomingImage.height()

        if self.timestamp:
            p = QPainter(incomingImage)
            p.setPen(QPen(self.timestamp_color))
            p.setFont(QFont("Times", self.timestamp_font_size, QFont.Bold))
            p.drawText(
                incomingImage.rect(),
                Qt.AlignHCenter,
                f'{datetime.now().strftime("%b-%d-%Y %H:%M:%S")}',
            )
            p.end()
            incomingImage = incomingImage.rgbSwapped()

        ptr = incomingImage.bits()
        ptr.setsize(self.height * self.width * 3)
        arr = np.frombuffer(ptr, np.uint8).reshape((self.height, self.width, 3))
        self.image_ready.emit(arr)
        # return arr

    def update_image_data(self, image: QImage):
        if self.recording and image:
            if (datetime.now() - self.start_time).seconds >= 3600 * self.hours_per_file:
                # Stop recording after x hours
                self._record()
                # Restart recording
                self._record()

            if self.raw_image:
                recorded_image = image.copy()
            else:
                pixmap = self.parent().grab()
                recorded_image = pixmap.toImage().convertToFormat(QImage.Format_RGB888)

            self.qimage_to_mat(recorded_image)

        return image

    def mouse_move_event(self, event: QMouseEvent):
        pass

    def mouse_press_event(self, event: QMouseEvent):
        pass

    def mouse_release_event(self, event: QMouseEvent):
        pass

    def context_menu_entry(self):
        actions = []
        label = "Stop recording" if self.recording else "Start recording"
        self.record_action = QAction(label, self.parent())
        self.record_action.triggered.connect(self._record)
        actions.append(self.record_action)
        return actions

    def _record(self):
        self.recording = not self.recording
        if self.recording:
            self.start_time = datetime.now()
            self.current_filepath = Path(self.filename.parent) / Path(
                f'{self.filename.stem}_{self.start_time.strftime("%b-%d-%Y_%H%M%S")}.{self.file_extension}'
            )
            print(f"Writing to {self.current_filepath}")
            # self.out = cv.VideoWriter(str(self.current_filepath), self.fourcc, 5.0, (self.width,self.height))
            self.video_recorder_thread.start(
                self.current_filepath, self.fourcc, self.fps, self.width, self.height
            )
        else:
            if not self.current_filepath:
                return
            self.video_recorder_thread.stop()
            self.video_recorder_thread.wait(500)
            self.end_time = datetime.now()
            self.new_filepath = Path(
                f'{self.current_filepath.stem}_{self.end_time.strftime("%b-%d-%Y_%H%M%S")}.{self.file_extension}'
            )
            self.current_filepath.rename(
                self.current_filepath.parent / self.new_filepath
            )
            print(
                f"Finished writing to {self.current_filepath.parent/self.new_filepath}"
            )
            self._update_files()

    def _update_files(self):
        """Function to check if number of files in the destination folder is correct
        Otherwise delete oldest file(s)
        """
        files_found = list(
            self.filename.parent.glob(f"{self.filename.stem}*.{self.file_extension}")
        )
        if len(files_found) > self.number_of_files:
            files_found = sorted(files_found, key=lambda f: f.stat().st_mtime, reverse=True)
            files_to_delete = files_found[self.number_of_files :]
            print(f"Files to delete: {files_to_delete}")
            for f in files_to_delete:
                f.unlink(missing_ok=True)

    def read_settings(self, settings: Dict[str, Any]):
        self.fps = int(settings.get("fps", 5))
        self.filename = Path(
            settings.get("path", Path.home()) / Path(settings.get("stem", "output"))
        )
        self.hours_per_file = int(settings.get("hours_per_file", 1))
        self.number_of_files = int(settings.get("number_of_files", 1))
        self.raw_image = True if settings.get("raw_image", "true") == "true" else False
        self.timestamp = True if settings.get("timestamp", "true") == "true" else False
        self.timestamp_color = settings.get(
            "timestamp_color", QColor.fromRgb(0, 255, 0)
        )
        self.timestamp_font_size = int(settings.get("timestamp_font_size", 12))
        self.width = int(settings.get("image_width", 480))

    def write_settings(self) -> Dict[str, Any]:
        settings = {}
        settings["fps"] = self.fps
        settings["path"] = self.filename.parent
        settings["stem"] = self.filename.stem
        settings["hours_per_file"] = self.hours_per_file
        settings["number_of_files"] = self.number_of_files
        settings["raw_image"] = self.raw_image
        settings["timestamp"] = self.timestamp
        settings["timestamp_color"] = self.timestamp_color
        settings["timestamp_font_size"] = self.timestamp_font_size
        settings["image_width"] = self.width
        return settings

    def start_plugin(self):
        pass

    def stop_plugin(self):
        pass

    def add_settings(self, parent=None) -> Optional[QGroupBox]:
        parent = parent if parent else self.parent()
        groupBox = QGroupBox(self.name, parent)
        layout = QFormLayout()

        self.base_path_widget = QLineEdit(str(self.filename.parent), parent)
        layout.addRow("Destination path", self.base_path_widget)

        self.file_prefix_widget = QLineEdit(str(self.filename.stem), parent)
        layout.addRow("File prefix", self.file_prefix_widget)

        ## Start row
        self.fps_widget = QSpinBox()
        self.fps_widget.setRange(1, 30)
        self.fps_widget.setValue(self.fps)

        self.image_width_widget = QSpinBox()
        self.image_width_widget.setRange(1, 4096)
        self.image_width_widget.setValue(self.width)

        hbox0 = QHBoxLayout()
        hbox0.addWidget(self.fps_widget)
        label0 = QLabel("Image width")
        hbox0.addWidget(label0)
        hbox0.addWidget(self.image_width_widget)
        layout.addRow("FPS", hbox0)
        ## End row

        ## Start row
        self.num_of_files_widget = QSpinBox()
        self.num_of_files_widget.setRange(1, 1000)
        self.num_of_files_widget.setValue(self.number_of_files)

        self.hours_per_file_widget = QSpinBox()
        self.hours_per_file_widget.setRange(1, 48)
        self.hours_per_file_widget.setValue(self.hours_per_file)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.hours_per_file_widget)
        label = QLabel("# of files")
        hbox1.addWidget(label)
        hbox1.addWidget(self.num_of_files_widget)
        layout.addRow("Hours per file", hbox1)
        ## End row

        ## Start row
        self.raw_image_widget = QCheckBox()
        self.raw_image_widget.setChecked(self.raw_image)
        label2 = QLabel("Add timestamp")
        self.timestamp_widget = QCheckBox()
        self.timestamp_widget.setChecked(self.timestamp)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.raw_image_widget)
        hbox2.addWidget(label2)
        hbox2.addWidget(self.timestamp_widget)

        layout.addRow("Record without overlays", hbox2)
        ## End row

        ## Start row
        self.timestamp_color_widget = ColorButton(
            parent=parent, color=self.timestamp_color
        )
        self.timestamp_font_size_widget = QSpinBox()
        self.timestamp_font_size_widget.setRange(1, 100)
        self.timestamp_font_size_widget.setValue(int(self.timestamp_font_size))
        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.timestamp_color_widget)
        hbox3.addWidget(QLabel("Timestamp font size"))
        hbox3.addWidget(self.timestamp_font_size_widget)
        layout.addRow("Timestamp color", hbox3)
        ## End row

        groupBox.setLayout(layout)
        return groupBox

    def save_settings(self, settings_groupbox):
        if not self.file_prefix_widget.text():
            prefix = "output"
        else:
            prefix = self.file_prefix_widget.text()

        try:
            base_path = Path(self.base_path_widget.text())
        except:
            base_path = Path.home()

        self.filename = base_path / Path(prefix)
        self.width = self.image_width_widget.value()
        self.fps = self.fps_widget.value()
        self.number_of_files = self.num_of_files_widget.value()
        self.hours_per_file = self.hours_per_file_widget.value()
        self.raw_image = self.raw_image_widget.isChecked()
        self.timestamp = self.timestamp_widget.isChecked()
        self.timestamp_color = self.timestamp_color_widget.color()
        self.timestamp_font_size = self.timestamp_font_size_widget.value()
