import threading
import mss
from time import time, sleep
import cv2
import numpy as np
import os
from collections import deque

from config import ROOT_DIR

class VideoHandler:
    def __init__(self):
        self.fps = 1 # Gemini only supports 1 fps
        self.recording_thread = None
        self.stop_event = threading.Event()
        self.video_path = os.path.join(ROOT_DIR, "temp", "screen_capture.mp4")
        self.frames = deque(maxlen=10)

    def _capture_loop(self):
        """Thread-safe capture loop"""
        # Initialize MSS and OpenCV in the same thread
        with mss.mss() as sct:
            monitor = sct.monitors[-1]
            
            while not self.stop_event.is_set():
                try:
                    # Capture frame
                    img = sct.grab(monitor)
                    img = np.array(img)
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    small_img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
                    self.frames.append(small_img)
                    sleep(1)

                except Exception as e:
                    print(f"Capture error: {str(e)}")
                    break

            if self.frames:
                height, width = self.frames[0].shape[:2]
                video = cv2.VideoWriter(
                    self.video_path, 
                    cv2.VideoWriter.fourcc(*'mp4v'), 
                    self.fps, 
                    (width, height)
                )
                for frame in self.frames:
                    video.write(frame)
                if video and video.isOpened():
                    video.release()

    def start_recording(self):
        """Start recording in background thread"""
        if not self.recording_thread or not self.recording_thread.is_alive():
            self.stop_event.clear()
            self.recording_thread = threading.Thread(
                target=self._capture_loop,
                daemon=True
            )
            self.recording_thread.start()
            print("System: Recording started")

    def stop_recording(self):
        """Signal thread to stop"""
        self.stop_event.set()
        if self.recording_thread:
            self.recording_thread.join(timeout=2)
        print("System: Recording stopped")