from typing import Dict, Any, TYPE_CHECKING
from qtpy.QtWidgets import QAction
from qtpy.QtGui import QImage
from microscope.plugins.base_plugin import BaseImagePlugin
from qtpy.QtGui import QMouseEvent
import cv2 as cv
import numpy as np
if TYPE_CHECKING:
    from microscope.microscope import Microscope

class RecordPlugin(BaseImagePlugin):
    def __init__(self, parent: "Microscope") -> None:
        super().__init__(parent)
        self.parent = parent
        self.name = 'Record'
        self.fourcc = cv.VideoWriter_fourcc(*'MJPG')
        self.filename = '/nsls2/data/mx/video_test/output.mjpg'
        self.recording = False
    
    def qimage_to_mat(self, incomingImage):
        '''  Converts a QImage into an opencv MAT format  '''

        incomingImage = incomingImage.convertToFormat(QImage.Format.Format_RGB32)

        width = incomingImage.width()
        height = incomingImage.height()

        ptr = incomingImage.bits()
        ptr.setsize(height * width * 4)
        arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))
        return arr
    
    def update_image_data(self, image: QImage):
        if self.recording and image:
            self.out.write(self.qimage_to_mat(image))
        return image

    def mouse_move_event(self, event: QMouseEvent):
        pass

    def mouse_press_event(self, event: QMouseEvent):
        pass

    def mouse_release_event(self, event: QMouseEvent):
        pass

    def context_menu_entry(self):
        actions = []
        label = 'Stop recording' if self.recording else 'Start recording'
        self.record_action = QAction(label, self.parent)
        self.record_action.triggered.connect(self._record)
        actions.append(self.record_action)
        return actions

    def _record(self):
        self.recording = not self.recording
        if self.recording:
            self.out = cv.VideoWriter(self.filename, self.fourcc, 5.0, (1280,720))
        else:
            self.out.release()


    def read_settings(self, settings: Dict[str, Any]):
        pass

    def write_settings(self) -> Dict[str, Any]:
        return {}