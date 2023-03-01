import time
from qtpy.QtCore import Signal, QByteArray, QObject, QUrl, QThread, Qt, QRect, QRectF
from qtpy.QtGui import QImage, QPainter, QBrush, QPen, QPixmap
from qtpy.QtNetwork import QNetworkReply, QNetworkRequest, QNetworkAccessManager
from typing import List, Any, Dict, Optional, NamedTuple
from cv2 import VideoCapture
import urllib.request
from io import BytesIO
from PIL import Image, ImageQt, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True


class Downloader(QObject):
    imageReady = Signal(object)

    def __init__(self, parent: "QObject|None" = None) -> None:
        super(Downloader, self).__init__(parent)
        self.manager = QNetworkAccessManager()
        self.url: str = "http://localhost:9998/jpg/image.jpg"
        self.request = QNetworkRequest()
        self.request.setUrl(QUrl(self.url))
        self.buffer = QByteArray()
        self.reply: Optional[QNetworkReply] = None
        self.isMjpegFeed = False

    def setUrl(self, url: str) -> None:
        self.url = url
        self.request.setUrl(QUrl(self.url))
        if self.url.lower().endswith("mjpg") or self.url.lower().endswith("cgi"):
            self.isMjpegFeed = True
            self.mjpegCamera = VideoCapture(self.url)
        else:
            self.isMjpegFeed = False
            self.mjpegCamera = None

    def downloadData(self) -> None:
        """Only request a new image if this is the first/last completed."""
        if self.reply is None and not self.isMjpegFeed:
            self.reply = self.manager.get(self.request)
            self.reply.finished.connect(self.finished)
        elif self.isMjpegFeed:
            if self.mjpegCamera:
                retVal, currentFrame = self.mjpegCamera.read()
                if currentFrame is not None:
                    height, width = currentFrame.shape[:2]
                    image = QImage(
                        currentFrame, width, height, 3 * width, QImage.Format_RGB888
                    )
                    self.imageReady.emit(image.rgbSwapped())

    def finished(self) -> None:
        """Read the buffer, emit a signal with the new image in it."""
        if self.reply:
            self.buffer = self.reply.readAll()
            self.imageReady.emit(self.buffer)
            self.reply.deleteLater()
            self.reply = None


class VideoThread(QThread):
    imageReady = Signal(object)

    def camera_refresh(self):
        """Only request a new image if this is the first/last completed."""
        if not self.isMjpegFeed:
            try:
                file = BytesIO(
                    urllib.request.urlopen(self.url, timeout=1000 / self.fps).read()
                )
                img = Image.open(file)
                qimage = ImageQt.ImageQt(img)
                self.showing_error = False
                self.imageReady.emit(qimage)
            except urllib.error.URLError:
                qimage = self.draw_message(f"URLError: {self.url}")
                self.imageReady.emit(qimage)
            except TimeoutError:
                qimage = self.draw_message(f"Timeout Error: {self.url}")
                self.imageReady.emit(qimage)
            except OSError as e:
                qimage = self.draw_message(f"OSError {e}: {self.url}")
                self.imageReady.emit(qimage)
            except Exception as e:
                qimage = self.draw_message(f"Exception {e}: {self.url}")
                self.imageReady.emit(qimage)

        elif self.isMjpegFeed and self.mjpegCamera:
            retVal, currentFrame = self.mjpegCamera.read()
            if currentFrame is not None:
                height, width = currentFrame.shape[:2]
                image = QImage(
                    currentFrame, width, height, 3 * width, QImage.Format_RGB888
                )
                self.imageReady.emit(image.rgbSwapped())
                # self.imageReady.emit(currentFrame)

    def __init__(self, *args, fps=5, url="", parent=None, **kwargs):
        # QThread.__init__(self, *args, **kwargs)
        super().__init__(parent)
        self.fps = fps
        self.url = url
        self.showing_error = False
        self.manager = QNetworkAccessManager(self)
        self.request = QNetworkRequest()
        self.request.setUrl(QUrl(self.url))
        self.buffer = QByteArray()
        self.reply: Optional[QNetworkReply] = None
        self.isMjpegFeed = False
        self.acquire = True

        self.error_qimage = QPixmap(400, 400).toImage()
        self.painter = QPainter(self.error_qimage)
        self.painter.setBrush(QBrush(Qt.green))
        self.painter.fillRect(QRectF(0, 0, 1000, 1000), Qt.green)
        self.painter.fillRect(QRectF(100, 100, 200, 100), Qt.white)
        self.painter.setPen(QPen(Qt.black))

    def setUrl(self, url: str) -> None:
        self.url = url
        self.request.setUrl(QUrl(self.url))
        if self.url.lower().endswith("mjpg") or self.url.lower().endswith("cgi"):
            self.isMjpegFeed = True
            self.mjpegCamera = VideoCapture(self.url)
        else:
            self.isMjpegFeed = False
            self.mjpegCamera = None

    def setFPS(self, fps: int) -> None:
        self.fps = fps

    def updateCam(self, camera_object):
        self.camera_object = camera_object

    def run(self):
        while self.acquire:
            self.camera_refresh()
            self.msleep(int(1000 / self.fps))

    def start(self):
        self.acquire = True
        super().start()

    def stop(self):
        self.acquire = False

    def draw_message(self, message: str) -> QImage:
        self.painter.drawText(QRectF(100, 100, 200, 100), message)
        return self.error_qimage
