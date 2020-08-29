import os
import pyautogui as pg

class ZoomUtilsMixin:
    """
    Basic manipulations of the Zoom UI. These methods are encapsulated into
    usable functions by the adjacent files.
    """
    def __init__(self, auto_prime=True):
        """
        If auto prime is true, pyautogui will find the full screen button and
        click on it, for more predictable placement of UI elements. 
        """
        self.is_participant_window_open = False
        pass

    def get_participant_window_position(self):
        needleImage = os.path.join(os.path.dirname(__file__), 'assets', 'small.png')
        try:
            res = pg.locateCenterOnScreen(needleImage)
        except:
            # image not found on screen; particpant window attribute is out of sync
            # with reality
            self._toogle_participant_window()
            self.is_participant_window_open = not self.is_participant_window_open
            res = pg.locateCenterOnScreen()
        return self._fix_point(res)

    def toggle_participation_window(self):
        pg.hotkey('command', 'u')
        self.is_participant_window_open = not self.is_participant_window_open
        return self.is_participant_window_open

    def _fix_point(self, point):
        """
        Points have a scaling issue on my mac. The values need to be divided by two.
        """
        # TODO add a check for operating system, because I think this only needs to be done on mac.
        return ((point.x // 2), (point.y // 2))