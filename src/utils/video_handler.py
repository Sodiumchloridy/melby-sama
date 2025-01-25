import threading
import mss
from time import time, sleep
import cv2
import numpy as np

class VideoHandler:
    def __init__(self):
        self.monitor = None  # Will be initialized in thread
        self.fps = 1
        self.video = None
        self.recording_thread = None
        self.stop_event = threading.Event()
        self.video_path = "screen_capture.mp4"

    def _capture_loop(self):
        """Thread-safe capture loop"""
        # Initialize MSS and OpenCV in the same thread
        with mss.mss() as sct:
            self.monitor = sct.monitors[-1]
            frame_size = (self.monitor['width']//2, self.monitor['height']//2)
            
            self.video = cv2.VideoWriter(
                self.video_path,
                cv2.VideoWriter_fourcc(*'mp4v'),
                self.fps,
                frame_size
            )

            frame_delta = 1.0 / self.fps
            next_frame = time()
            
            while not self.stop_event.is_set():
                try:
                    # Capture frame
                    img = sct.grab(self.monitor)
                    img = np.array(img)
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    small = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
                    self.video.write(small)

                    # Timing control
                    now = time()
                    if now < next_frame:
                        sleep(next_frame - now)
                    next_frame += frame_delta

                except Exception as e:
                    print(f"Capture error: {str(e)}")
                    break

            if self.video and self.video.isOpened():
                self.video.release()
            cv2.destroyAllWindows()

    def start_recording(self):
        """Start recording in background thread"""
        if not self.recording_thread or not self.recording_thread.is_alive():
            self.stop_event.clear()
            self.recording_thread = threading.Thread(
                target=self._capture_loop,
                daemon=True
            )
            self.recording_thread.start()
            print("Recording started")

    def stop_recording(self):
        """Signal thread to stop"""
        self.stop_event.set()
        if self.recording_thread:
            self.recording_thread.join(timeout=2)
        print("Recording stopped")