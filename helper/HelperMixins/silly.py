from time import sleep
from subprocess import call
import sys


class SillyMixin:
    def __init__(self, *args, **kwargs):
        pass

    def timer(self, time_mins: int, alarm_message: str):
        if sys.platform != "darwin":
            raise Exception(
                "This function only works on Darwin platforms (OS X)")
        sleep(time_mins * 60)
        args = ['say'] + alarm_message.split(' ')
        for _ in range(3):
            print('Timer ended')
            subprocess.call(args)
            sleep(3)
