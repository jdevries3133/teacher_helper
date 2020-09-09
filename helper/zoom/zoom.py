import os
import pyautogui as pg

from .utils import ZoomUtilsMixin


class Zoom(ZoomUtilsMixin):
    def __init__(self):
        super().__init__()

    def take_attendance(self):
        if not self.is_participant_window_open:
            self.toggle_participation_window()

    def rename_student(self, student_name, new_name):
        if not self.is_participant_window_open:
            self.toggle_participation_window()
        participant_window_location = self.find_participant_window()

