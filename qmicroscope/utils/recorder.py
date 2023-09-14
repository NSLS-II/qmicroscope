import cv2
import requests
import numpy as np
import threading
import time
from epics import PV


class VideoWriter:
    def __init__(self, url, fps, output_path, epics_pv_name=None):
        self.url = url
        self.fps = fps
        self.output_path = output_path
        self.epics_pv_name = epics_pv_name
        if epics_pv_name:
            self.epics_pv = PV(epics_pv_name)
            self.epics_pv.add_callback(self._watch_pv)
        self.fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.current_image = None
        self.is_recording = False
        self.writer_thread = None
        self.reader_thread = None

    def get_image_from_url(self):
        try:
            response = requests.get(self.url, stream=True)
            response.raise_for_status()
            image = np.asarray(bytearray(response.content), dtype="uint8")
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)
            return image
        except requests.HTTPError:
            print(f"HTTP GET request to url {self.url} failed.")
        except Exception as e:
            print(
                f"An error occurred while trying to retrieve an image from the url {self.url}: {str(e)}"
            )
        return None

    def start_recording(self):
        self.is_recording = True
        self.writer_thread = threading.Thread(target=self._writer_loop)
        self.writer_thread.start()
        self.reader_thread = threading.Thread(target=self._reader_loop)
        self.reader_thread.start()

    def stop_recording(self):
        self.is_recording = False
        if self.writer_thread:
            self.writer_thread.join()
        if self.reader_thread:
            self.reader_thread.join()

    def _watch_pv(self, **kwargs):
        if kwargs["pvname"] != self.epics_pv_name:
            return
        if kwargs["value"] == 1 and not self.is_recording:
            print(f"{self.epics_pv_name} : {kwargs['value']}. START record action")
            self.start_recording()
        elif kwargs["value"] == 0 and self.is_recording:
            print(f"{self.epics_pv_name} : {kwargs['value']}. STOP record action")
            self.stop_recording()

    def _reader_loop(self):
        while self.is_recording:
            image = self.get_image_from_url()
            if image is not None:
                self.current_image = image
            time.sleep(1.0 / self.fps)

    def _writer_loop(self):
        out = None
        frame_size = None
        frame_period = 1.0 / self.fps
        while self.is_recording:
            if self.current_image is not None:
                if out is None:
                    frame_size = (
                        self.current_image.shape[1],
                        self.current_image.shape[0],
                    )
                    out = cv2.VideoWriter(
                        self.output_path, self.fourcc, self.fps, frame_size
                    )
                out.write(self.current_image)
            time.sleep(frame_period)
        if out is not None:
            out.release()


if __name__ == "__main__":
    # Usage
    url = "http://localhost:8080/output.jpg"
    fps = 10
    output_file_path = "output.mp4"
    pv_name = "XF:17IDB-ES:AMX{Stills}-Stat"
    video_writer = VideoWriter(url, fps, output_file_path, epics_pv_name=pv_name)

    # PV Name is optional. If not using PV name you can start or stop recording like so
    """
    video_writer.start_recording()
    time.sleep(10)  # Let it record for 10 seconds
    video_writer.stop_recording()
    """

    # Otherwise you would run your script and as long as the program is alive the PV will
    # start and stop the recording. In this example, the program is kept alive using
    # an infinite loop
    while True:
        pass
