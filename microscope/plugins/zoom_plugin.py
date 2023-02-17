from qtpy.QtWidgets import QAction, QWidget
from qtpy.QtCore import QRect, Qt

from typing import Any, Dict, Optional

from microscope.widgets.rubberband import ResizableRubberBand
from microscope.plugins.base_plugin import BaseImagePlugin

class ZoomPlugin(BaseImagePlugin):

    def __init__(self, parent: "Optional[QWidget]"=None):
        super().__init__(parent)
        self.name = 'Zoom'
        self.zoomRubberBand: "Optional[ResizableRubberBand]" = None
        self.startCrop = False
        self.parent = parent
        self.crop = None

    def _crop_image(self) -> None:
        if self.zoomRubberBand:
            width_scaling_factor = self.org_image_wd/self.parent.image.width()
            ht_scaling_factor = self.org_image_ht/self.parent.image.height()
            
            rect_x, rect_y, rect_width, rect_ht = self.zoomRubberBand.geometry().getRect()
            x = int(rect_x*width_scaling_factor)
            y = int(rect_y*ht_scaling_factor)
            wd = int(rect_width*width_scaling_factor)
            ht = int(rect_ht*ht_scaling_factor)  
            self.crop = QRect(x,y,wd,ht)
            self.zoomRubberBand.hide()
            #self.zoomRubberBand.destroy()
            self.zoomRubberBand = None

    def _start_crop(self):
        self.startCrop = True
        if self.parent:
            self.parent.setCursor(Qt.CrossCursor)

    def context_menu_entry(self):
        actions = []
        self.crop_action = QAction('Zoom/Crop to selection', self.parent)
        self.crop_action.triggered.connect(self._start_crop)
        actions.append(self.crop_action)
        if self.crop:
            self.reset_crop_action = QAction('Reset Zoom/Crop', self.parent)
            self.reset_crop_action.triggered.connect(self._reset_crop)
            actions.append(self.reset_crop_action)
        return actions

    def mouse_press_event(self, event):
        if not self.zoomRubberBand and self.startCrop and event.buttons() == Qt.LeftButton:
            self.zoomRubberBand = ResizableRubberBand(self.parent)
            self.temp_start = event.pos()

    def mouse_move_event(self, event):
        if self.startCrop and event.buttons() == Qt.LeftButton:
            self.zoomRubberBand.show()
            self.zoomRubberBand.setGeometry(QRect(self.temp_start, event.pos()).normalized())

    def mouse_release_event(self, event):
        if self.startCrop:
            self._crop_image()
            self.startCrop = False
            self.parent.unsetCursor()

    def update_image_data(self, image):
        self.org_image_ht = image.height()
        self.org_image_wd = image.width()
        if self.crop:
            image = image.copy(self.crop)
        return image

    def _reset_crop(self) -> None:
        self.crop = None

    def read_settings(self, settings: Dict[str, Any]):
        self.crop = settings.get('crop', None)
        

    def write_settings(self) -> Dict[str, Any]:
        return {'crop': self.crop}
