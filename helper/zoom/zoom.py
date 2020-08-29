import os
import pyautogui as pg

from .utils import ZoomUtilsMixin


class ZoomAttendance(ZoomUtilsMixin):
    def __init__(self):
        super().__init__()

    def take_attendance(self):
        if not self.is_participant_window_open:
            self._toggle_participation_window()
        pass
